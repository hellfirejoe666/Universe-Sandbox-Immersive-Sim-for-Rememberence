"""
Donjon-style text generator - Python port
Public domain logic from drow@bin.sh
"""

import random
import json
import os

class DonjonTextGenerator:
    """Token-based text generator like donjon.bin.sh"""
    
    def __init__(self, data_dir=None):
        self.data_dir = data_dir or os.path.dirname(__file__)
        self.gen_data = {}
        self.name_set = {}
        self.chain_cache = {}
        
    def load_json(self, filename, data_type='text'):
        """Load JSON data file"""
        path = os.path.join(self.data_dir, filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data_type == 'text':
                    self.gen_data[filename] = data
                elif data_type == 'names':
                    self.name_set[filename] = data
                return True
        except FileNotFoundError:
            print(f"Warning: {path} not found")
            return False
    
    def select_from(self, lst):
        """Select random item from list or weighted table"""
        if isinstance(lst, list):
            return random.choice(lst)
        elif isinstance(lst, dict):
            # Weighted table with range keys like "1-50", "51-00"
            return self._select_from_table(lst)
        return None
    
    def _select_from_table(self, table):
        """Select from weighted table with range keys"""
        max_val = self._scale_table(table)
        if max_val == 0:
            return None
        idx = random.randint(1, max_val)
        
        for key, value in table.items():
            r = self._key_range(key)
            if r and idx >= r[0] and idx <= r[1]:
                return value
        return None
    
    def _scale_table(self, table):
        """Get max value from table"""
        max_len = 0
        for key in table.keys():
            r = self._key_range(key)
            if r and r[1] > max_len:
                max_len = r[1]
        return max_len
    
    def _key_range(self, key):
        """Parse range key like '1-50' or '51-00' or '25'"""
        import re
        match = re.match(r'(\d+)-00', key)
        if match:
            return [int(match.group(1)), 100]
        match = re.match(r'(\d+)-(\d+)', key)
        if match:
            return [int(match.group(1)), int(match.group(2))]
        if key == '00':
            return [100, 100]
        try:
            val = int(key)
            return [val, val]
        except ValueError:
            return None
    
    def expand_tokens(self, string, depth=0):
        """Expand {token} placeholders recursively"""
        if depth > 10:  # Prevent infinite recursion
            return string
        
        import re
        while True:
            match = re.search(r'{(\w+)}', string)
            if not match:
                break
            
            token = match.group(1)
            repl = self.generate_text(token)
            
            if repl:
                string = string.replace('{' + token + '}', repl, 1)
            else:
                # Token not found, remove braces
                string = string.replace('{' + token + '}', token, 1)
        
        return string
    
    def generate_text(self, type_name):
        """Generate text of given type"""
        if type_name in self.gen_data:
            result = self.select_from(self.gen_data[type_name])
            if result:
                return self.expand_tokens(result)
        return ''
    
    def generate_list(self, type_name, n):
        """Generate multiple items"""
        return [self.generate_text(type_name) for _ in range(n)]
    
    # Markov chain name generation
    def generate_name(self, type_name):
        """Generate a name using Markov chain"""
        chain = self._get_markov_chain(type_name)
        if chain:
            return self._markov_name(chain)
        return ''
    
    def _get_markov_chain(self, type_name):
        """Get or build Markov chain for name type"""
        if type_name in self.chain_cache:
            return self.chain_cache[type_name]
        
        if type_name not in self.name_set:
            return None
        
        name_list = self.name_set[type_name]
        if not name_list:
            return None
        
        chain = self._construct_chain(name_list)
        self.chain_cache[type_name] = chain
        return chain
    
    def _construct_chain(self, name_list):
        """Build Markov chain from list of names"""
        chain = {}
        
        for names_str in name_list:
            names = names_str.split()
            chain = self._incr_chain(chain, 'parts', len(names))
            
            for name in names:
                chain = self._incr_chain(chain, 'name_len', len(name))
                if name:
                    chain = self._incr_chain(chain, 'initial', name[0])
                    
                    last_c = name[0]
                    for c in name[1:]:
                        chain = self._incr_chain(chain, last_c, c)
                        last_c = c
        
        return self._scale_chain(chain)
    
    def _incr_chain(self, chain, key, token):
        """Increment chain counter"""
        if key not in chain:
            chain[key] = {}
        if token not in chain[key]:
            chain[key][token] = 1
        else:
            chain[key][token] += 1
        return chain
    
    def _scale_chain(self, chain):
        """Apply weighting to chain"""
        for key in chain:
            for token in chain[key]:
                count = chain[key][token]
                chain[key][token] = int(count ** 1.3)
        return chain
    
    def _markov_name(self, chain):
        """Generate name from Markov chain"""
        if 'initial' not in chain:
            return ''
        
        # Pick initial letter
        initials = list(chain['initial'].keys())
        weights = list(chain['initial'].values())
        initial = random.choices(initials, weights=weights)[0]
        
        name = initial
        max_len = 12  # Reasonable name length
        
        while len(name) < max_len:
            last_char = name[-1]
            if last_char not in chain:
                break
            
            options = list(chain[last_char].keys())
            if not options:
                break
            
            weights = list(chain[last_char].values())
            next_char = random.choices(options, weights=weights)[0]
            
            # End name sometimes
            if random.random() < 0.3 and len(name) > 3:
                break
            
            name += next_char
        
        return name.capitalize()
