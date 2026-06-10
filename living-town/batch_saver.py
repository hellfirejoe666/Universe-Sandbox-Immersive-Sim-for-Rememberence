"""
Batch Saver with Async Support for Older Machines

Saves data in batches to avoid blocking gameplay.
Optimized for low memory and minimal I/O overhead.
"""

import json
import threading
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class BatchSaver:
    """
    Saves data in batches to minimize I/O overhead.
    
    Optimized for older machines:
    - Batches multiple entities per save
    - Optional async saves (non-blocking)
    - Progressive saving (don't save everything at once)
    """
    
    def __init__(self, save_dir: str = None, batch_size: int = 100, 
                 async_enabled: bool = True):
        if save_dir is None:
            save_dir = str(Path(__file__).parent / 'saves')
        
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        self.batch_size = batch_size
        self.async_enabled = async_enabled
        
        # Pending saves
        self.pending_narratives = []
        self.pending_events = []
        self.pending_entities = {}
        
        # Async thread
        self.save_thread = None
        self.save_queue = []
        
        # Statistics
        self.total_saves = 0
        self.total_time = 0
        self.async_saves = 0
    
    def queue_narrative(self, entity_id: str, narrative_data: Dict):
        """Queue narrative for batch save."""
        self.pending_narratives.append({
            'entity_id': entity_id,
            'data': narrative_data,
            'queued_at': datetime.now().isoformat()
        })
        
        # Auto-save if batch full
        if len(self.pending_narratives) >= self.batch_size:
            self.flush_narratives()
    
    def queue_event(self, event_data: Dict):
        """Queue event for batch save."""
        self.pending_events.append({
            'data': event_data,
            'queued_at': datetime.now().isoformat()
        })
        
        # Auto-save if batch full
        if len(self.pending_events) >= self.batch_size:
            self.flush_events()
    
    def queue_entity(self, entity_type: str, entity_id: str, entity_data: Dict):
        """Queue entity for batch save."""
        key = f"{entity_type}_{entity_id}"
        self.pending_entities[key] = {
            'type': entity_type,
            'id': entity_id,
            'data': entity_data,
            'queued_at': datetime.now().isoformat()
        }
        
        # Auto-save if batch full
        if len(self.pending_entities) >= self.batch_size:
            self.flush_entities()
    
    def flush_narratives(self, force: bool = False):
        """Flush pending narratives to disk."""
        if not self.pending_narratives and not force:
            return
        
        start = time.time()
        
        # Save to file
        filename = f"narratives_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.save_dir / filename
        
        data = {
            'saved_at': datetime.now().isoformat(),
            'count': len(self.pending_narratives),
            'narratives': {
                n['entity_id']: n['data'] for n in self.pending_narratives
            }
        }
        
        self._save_json(filepath, data)
        
        elapsed = time.time() - start
        self.total_saves += 1
        self.total_time += elapsed
        
        print(f"[BatchSaver] Saved {len(self.pending_narratives)} narratives in {elapsed:.2f}s")
        
        self.pending_narratives = []
    
    def flush_events(self, force: bool = False):
        """Flush pending events to disk."""
        if not self.pending_events and not force:
            return
        
        start = time.time()
        
        filename = f"events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.save_dir / filename
        
        data = {
            'saved_at': datetime.now().isoformat(),
            'count': len(self.pending_events),
            'events': self.pending_events
        }
        
        self._save_json(filepath, data)
        
        elapsed = time.time() - start
        self.total_saves += 1
        self.total_time += elapsed
        
        print(f"[BatchSaver] Saved {len(self.pending_events)} events in {elapsed:.2f}s")
        
        self.pending_events = []
    
    def flush_entities(self, force: bool = False):
        """Flush pending entities to disk."""
        if not self.pending_entities and not force:
            return
        
        start = time.time()
        
        filename = f"entities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.save_dir / filename
        
        data = {
            'saved_at': datetime.now().isoformat(),
            'count': len(self.pending_entities),
            'entities': self.pending_entities
        }
        
        self._save_json(filepath, data)
        
        elapsed = time.time() - start
        self.total_saves += 1
        self.total_time += elapsed
        
        print(f"[BatchSaver] Saved {len(self.pending_entities)} entities in {elapsed:.2f}s")
        
        self.pending_entities = {}
    
    def flush_all(self):
        """Flush all pending saves."""
        print("[BatchSaver] Flushing all pending saves...")
        self.flush_narratives(force=True)
        self.flush_events(force=True)
        self.flush_entities(force=True)
    
    def _save_json(self, filepath: Path, data: Dict):
        """Save JSON to file."""
        if self.async_enabled and len(self.save_queue) < 3:
            # Async save (non-blocking)
            self.save_queue.append((filepath, data))
            
            if self.save_thread is None or not self.save_thread.is_alive():
                self.save_thread = threading.Thread(target=self._process_queue, daemon=True)
                self.save_thread.start()
                self.async_saves += 1
        else:
            # Sync save (blocking, but safer for very old machines)
            filepath.write_text(json.dumps(data, indent=2, default=str), encoding='utf-8')
    
    def _process_queue(self):
        """Process async save queue."""
        while self.save_queue:
            filepath, data = self.save_queue.pop(0)
            try:
                filepath.write_text(json.dumps(data, indent=2, default=str), encoding='utf-8')
            except Exception as e:
                print(f"[BatchSaver] Async save failed: {e}")
    
    def stats(self) -> Dict[str, Any]:
        """Get save statistics."""
        avg_time = (self.total_time / self.total_saves) if self.total_saves > 0 else 0
        
        return {
            'total_saves': self.total_saves,
            'async_saves': self.async_saves,
            'sync_saves': self.total_saves - self.async_saves,
            'avg_save_time': f"{avg_time:.2f}s",
            'pending_narratives': len(self.pending_narratives),
            'pending_events': len(self.pending_events),
            'pending_entities': len(self.pending_entities),
            'batch_size': self.batch_size
        }


# ────────────────────────────────────────────────
# Test
# ────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 60)
    print("BATCH SAVER TEST (Old Machine Optimized)")
    print("=" * 60)
    
    saver = BatchSaver(batch_size=5, async_enabled=True)
    
    # Test narrative batching
    print("\n[1/3] Testing Narrative Batching...")
    
    for i in range(7):
        saver.queue_narrative(f'npc_{i:03d}', {
            'text': f'Narrative for NPC {i}',
            'generated_at': datetime.now().isoformat()
        })
        print(f"  Queued narrative {i+1}/7")
    
    # Should have auto-saved at 5, then 2 pending
    print(f"  Pending: {len(saver.pending_narratives)}")
    
    # Flush remaining
    saver.flush_narratives(force=True)
    
    # Test event batching
    print("\n[2/3] Testing Event Batching...")
    
    for i in range(3):
        saver.queue_event({
            'week': i+1,
            'action': f'Event {i+1}',
            'success': i % 2 == 0
        })
        print(f"  Queued event {i+1}/3")
    
    # Flush events
    saver.flush_events(force=True)
    
    # Test statistics
    print("\n[3/3] Save Statistics...")
    stats = saver.stats()
    
    print(f"  Total Saves: {stats['total_saves']}")
    print(f"  Async Saves: {stats['async_saves']}")
    print(f"  Avg Save Time: {stats['avg_save_time']}")
    print(f"  Batch Size: {stats['batch_size']}")
    
    print("\n" + "=" * 60)
    print("BATCH SAVER TEST COMPLETE")
    print("=" * 60)
