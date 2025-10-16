"""Supabase client for real-time features and auth."""

import os
import logging
from typing import Optional, Dict, Any, Callable
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class SupabaseManager:
    """Manages Supabase connection and real-time subscriptions."""
    
    def __init__(
        self,
        url: Optional[str] = None,
        key: Optional[str] = None
    ):
        """
        Initialize Supabase client.
        
        Args:
            url: Supabase project URL (or from SUPABASE_URL env)
            key: Supabase anon/service key (or from SUPABASE_KEY env)
        """
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            logger.warning("Supabase credentials not configured. Real-time features disabled.")
            self.client = None
        else:
            self.client: Client = create_client(self.url, self.key)
            logger.info("Supabase client initialized")
    
    def is_available(self) -> bool:
        """Check if Supabase is configured."""
        return self.client is not None
    
    # Authentication
    
    def sign_up_rater(self, email: str, password: str, metadata: Dict[str, Any] = None) -> Dict:
        """Sign up a new rater."""
        if not self.client:
            raise RuntimeError("Supabase not configured")
        
        response = self.client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": metadata or {}
            }
        })
        return response
    
    def sign_in_rater(self, email: str, password: str) -> Dict:
        """Sign in a rater."""
        if not self.client:
            raise RuntimeError("Supabase not configured")
        
        response = self.client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return response
    
    def get_user(self) -> Optional[Dict]:
        """Get current authenticated user."""
        if not self.client:
            return None
        
        return self.client.auth.get_user()
    
    # Real-time Subscriptions
    
    def subscribe_to_new_tasks(
        self,
        callback: Callable[[Dict], None],
        rater_id: Optional[str] = None
    ):
        """
        Subscribe to new rating tasks.
        
        Args:
            callback: Function to call when new task arrives
            rater_id: Optional filter by rater
        """
        if not self.client:
            logger.warning("Supabase not available, skipping subscription")
            return
        
        channel = self.client.channel('rating_tasks')
        
        # Subscribe to inserts
        channel.on(
            'postgres_changes',
            event='INSERT',
            schema='public',
            table='rating_tasks',
            callback=lambda payload: callback(payload['record'])
        )
        
        channel.subscribe()
        logger.info("Subscribed to new rating tasks")
        return channel
    
    def subscribe_to_task_updates(
        self,
        task_id: str,
        callback: Callable[[Dict], None]
    ):
        """Subscribe to updates on a specific task."""
        if not self.client:
            return
        
        channel = self.client.channel(f'task_{task_id}')
        
        channel.on(
            'postgres_changes',
            event='UPDATE',
            schema='public',
            table='rating_tasks',
            filter=f'task_id=eq.{task_id}',
            callback=lambda payload: callback(payload['record'])
        )
        
        channel.subscribe()
        return channel
    
    def subscribe_to_rater_stats(
        self,
        rater_id: str,
        callback: Callable[[Dict], None]
    ):
        """Subscribe to rater statistics updates."""
        if not self.client:
            return
        
        channel = self.client.channel(f'rater_{rater_id}')
        
        channel.on(
            'postgres_changes',
            event='UPDATE',
            schema='public',
            table='rater_profiles',
            filter=f'rater_id=eq.{rater_id}',
            callback=lambda payload: callback(payload['record'])
        )
        
        channel.subscribe()
        return channel
    
    # Storage
    
    def upload_model_artifact(
        self,
        bucket: str,
        path: str,
        file_data: bytes
    ) -> Dict:
        """
        Upload model artifact to Supabase Storage.
        
        Args:
            bucket: Storage bucket name (e.g., 'model-artifacts')
            path: File path in bucket
            file_data: File bytes
        
        Returns:
            Upload response
        """
        if not self.client:
            raise RuntimeError("Supabase not configured")
        
        response = self.client.storage.from_(bucket).upload(
            path,
            file_data
        )
        return response
    
    def download_model_artifact(
        self,
        bucket: str,
        path: str
    ) -> bytes:
        """Download model artifact from Supabase Storage."""
        if not self.client:
            raise RuntimeError("Supabase not configured")
        
        response = self.client.storage.from_(bucket).download(path)
        return response
    
    def get_public_url(self, bucket: str, path: str) -> str:
        """Get public URL for a file."""
        if not self.client:
            raise RuntimeError("Supabase not configured")
        
        return self.client.storage.from_(bucket).get_public_url(path)
    
    # Database Operations (for real-time data)
    
    def insert_judgment_realtime(self, judgment_data: Dict) -> Dict:
        """Insert judgment with real-time broadcast."""
        if not self.client:
            raise RuntimeError("Supabase not configured")
        
        response = self.client.table('judgments').insert(judgment_data).execute()
        return response.data[0] if response.data else None
    
    def get_pending_tasks(
        self,
        limit: int = 10,
        rater_id: Optional[str] = None
    ) -> list:
        """Get pending tasks for assignment."""
        if not self.client:
            return []
        
        query = self.client.table('rating_tasks')\
            .select('*')\
            .eq('status', 'pending')\
            .order('priority', desc=True)\
            .limit(limit)
        
        response = query.execute()
        return response.data
    
    def update_task_status(
        self,
        task_id: str,
        status: str,
        **kwargs
    ) -> Dict:
        """Update task status (triggers real-time update)."""
        if not self.client:
            raise RuntimeError("Supabase not configured")
        
        update_data = {'status': status, **kwargs}
        response = self.client.table('rating_tasks')\
            .update(update_data)\
            .eq('task_id', task_id)\
            .execute()
        
        return response.data[0] if response.data else None
    
    # Edge Functions
    
    def invoke_edge_function(
        self,
        function_name: str,
        payload: Dict
    ) -> Dict:
        """
        Invoke Supabase Edge Function.
        
        Args:
            function_name: Name of edge function
            payload: Function payload
        
        Returns:
            Function response
        """
        if not self.client:
            raise RuntimeError("Supabase not configured")
        
        response = self.client.functions.invoke(
            function_name,
            invoke_options={'body': payload}
        )
        return response


# Global instance
_supabase_manager: Optional[SupabaseManager] = None


def init_supabase(url: Optional[str] = None, key: Optional[str] = None) -> SupabaseManager:
    """Initialize global Supabase manager."""
    global _supabase_manager
    _supabase_manager = SupabaseManager(url, key)
    return _supabase_manager


def get_supabase() -> SupabaseManager:
    """Get global Supabase manager."""
    if _supabase_manager is None:
        return init_supabase()
    return _supabase_manager


# Example usage in rater app
if __name__ == "__main__":
    # Initialize
    supabase = init_supabase()
    
    if supabase.is_available():
        # Subscribe to new tasks
        def handle_new_task(task):
            print(f"New task: {task['task_id']}")
        
        supabase.subscribe_to_new_tasks(handle_new_task)
        
        # Get pending tasks
        tasks = supabase.get_pending_tasks(limit=5)
        print(f"Found {len(tasks)} pending tasks")
        
        # Upload model
        with open("model.safetensors", "rb") as f:
            supabase.upload_model_artifact(
                "model-artifacts",
                "adapters/amazon_v1.safetensors",
                f.read()
            )
