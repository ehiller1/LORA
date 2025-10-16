"""Adapter manager for loading and composing LoRA adapters."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import json

from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch

logger = logging.getLogger(__name__)


@dataclass
class AdapterMetadata:
    """Metadata for a LoRA adapter."""
    adapter_id: str
    adapter_type: str  # retailer, brand, task
    name: str
    version: str
    path: Path
    dependencies: List[str]
    tags: Set[str]
    created_at: str
    
    @classmethod
    def from_file(cls, metadata_path: Path) -> "AdapterMetadata":
        """Load metadata from JSON file."""
        with open(metadata_path, 'r') as f:
            data = json.load(f)
        
        return cls(
            adapter_id=data["adapter_id"],
            adapter_type=data["adapter_type"],
            name=data["name"],
            version=data["version"],
            path=Path(data["path"]),
            dependencies=data.get("dependencies", []),
            tags=set(data.get("tags", [])),
            created_at=data["created_at"]
        )


class AdapterManager:
    """Manages LoRA adapter loading and composition."""
    
    def __init__(
        self,
        base_model_path: str,
        adapters_dir: Path,
        device: str = "auto"
    ):
        """Initialize adapter manager.
        
        Args:
            base_model_path: Path to base model
            adapters_dir: Directory containing adapters
            device: Device to run on
        """
        self.base_model_path = base_model_path
        self.adapters_dir = adapters_dir
        self.device = device
        
        # Registry of available adapters
        self.adapter_registry: Dict[str, AdapterMetadata] = {}
        
        # Loaded adapters cache
        self.loaded_adapters: Dict[str, PeftModel] = {}
        
        # Base model (loaded lazily)
        self.tokenizer: Optional[AutoTokenizer] = None
        self.base_model: Optional[AutoModelForCausalLM] = None
        
        # Discover adapters
        self._discover_adapters()
        
        logger.info(f"Adapter Manager initialized with {len(self.adapter_registry)} adapters")
    
    def _discover_adapters(self) -> None:
        """Discover available adapters in adapters directory."""
        if not self.adapters_dir.exists():
            logger.warning(f"Adapters directory not found: {self.adapters_dir}")
            return
        
        # Look for adapter metadata files
        for metadata_file in self.adapters_dir.rglob("adapter_metadata.json"):
            try:
                metadata = AdapterMetadata.from_file(metadata_file)
                self.adapter_registry[metadata.adapter_id] = metadata
                logger.info(f"Discovered adapter: {metadata.adapter_id} ({metadata.adapter_type})")
            except Exception as e:
                logger.error(f"Failed to load adapter metadata from {metadata_file}: {e}")
    
    def load_base_model(self) -> None:
        """Load base model if not already loaded."""
        if self.base_model is not None:
            return
        
        logger.info(f"Loading base model: {self.base_model_path}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.base_model_path,
            trust_remote_code=True
        )
        
        self.base_model = AutoModelForCausalLM.from_pretrained(
            self.base_model_path,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map=self.device,
            trust_remote_code=True
        )
        
        self.base_model.eval()
        logger.info("Base model loaded")
    
    def load_adapter(self, adapter_id: str) -> PeftModel:
        """Load a specific adapter.
        
        Args:
            adapter_id: Adapter identifier
            
        Returns:
            Model with adapter loaded
        """
        # Check if already loaded
        if adapter_id in self.loaded_adapters:
            logger.info(f"Adapter {adapter_id} already loaded")
            return self.loaded_adapters[adapter_id]
        
        # Check if adapter exists
        if adapter_id not in self.adapter_registry:
            raise ValueError(f"Adapter not found: {adapter_id}")
        
        metadata = self.adapter_registry[adapter_id]
        
        # Load base model if needed
        self.load_base_model()
        
        logger.info(f"Loading adapter: {adapter_id} from {metadata.path}")
        
        # Load adapter
        model_with_adapter = PeftModel.from_pretrained(
            self.base_model,
            str(metadata.path),
            is_trainable=False
        )
        
        self.loaded_adapters[adapter_id] = model_with_adapter
        logger.info(f"Adapter {adapter_id} loaded successfully")
        
        return model_with_adapter
    
    def compose_adapters(
        self,
        adapter_ids: List[str],
        composition_strategy: str = "sequential"
    ) -> PeftModel:
        """Compose multiple adapters.
        
        Args:
            adapter_ids: List of adapter IDs to compose
            composition_strategy: How to compose adapters (sequential, additive)
            
        Returns:
            Model with composed adapters
        """
        if not adapter_ids:
            raise ValueError("No adapters specified")
        
        logger.info(f"Composing adapters: {adapter_ids} (strategy: {composition_strategy})")
        
        # Load base model
        self.load_base_model()
        
        # For now, implement sequential composition (load adapters in order)
        # More sophisticated composition would require custom PEFT logic
        
        model = self.base_model
        for adapter_id in adapter_ids:
            if adapter_id not in self.adapter_registry:
                raise ValueError(f"Adapter not found: {adapter_id}")
            
            metadata = self.adapter_registry[adapter_id]
            logger.info(f"Adding adapter: {adapter_id}")
            
            model = PeftModel.from_pretrained(
                model,
                str(metadata.path),
                is_trainable=False
            )
        
        return model
    
    def get_adapters_by_type(self, adapter_type: str) -> List[AdapterMetadata]:
        """Get all adapters of a specific type.
        
        Args:
            adapter_type: Adapter type (retailer, brand, task)
            
        Returns:
            List of adapter metadata
        """
        return [
            metadata for metadata in self.adapter_registry.values()
            if metadata.adapter_type == adapter_type
        ]
    
    def get_adapters_by_tag(self, tag: str) -> List[AdapterMetadata]:
        """Get all adapters with a specific tag.
        
        Args:
            tag: Tag to search for
            
        Returns:
            List of adapter metadata
        """
        return [
            metadata for metadata in self.adapter_registry.values()
            if tag in metadata.tags
        ]
    
    def select_adapters_for_request(
        self,
        retailer_id: Optional[str] = None,
        brand_id: Optional[str] = None,
        task: Optional[str] = None
    ) -> List[str]:
        """Select appropriate adapters for a request.
        
        Args:
            retailer_id: Retailer identifier
            brand_id: Brand identifier
            task: Task name
            
        Returns:
            List of adapter IDs to use
        """
        selected = []
        
        # Select retailer adapter
        if retailer_id:
            retailer_adapters = [
                a for a in self.adapter_registry.values()
                if a.adapter_type == "retailer" and retailer_id in a.tags
            ]
            if retailer_adapters:
                selected.append(retailer_adapters[0].adapter_id)
        
        # Select brand adapter
        if brand_id:
            brand_adapters = [
                a for a in self.adapter_registry.values()
                if a.adapter_type == "brand" and brand_id in a.tags
            ]
            if brand_adapters:
                selected.append(brand_adapters[0].adapter_id)
        
        # Select task adapter
        if task:
            task_adapters = [
                a for a in self.adapter_registry.values()
                if a.adapter_type == "task" and task in a.tags
            ]
            if task_adapters:
                selected.append(task_adapters[0].adapter_id)
        
        logger.info(f"Selected adapters: {selected}")
        return selected
    
    def register_adapter(
        self,
        adapter_path: Path,
        adapter_type: str,
        name: str,
        tags: Optional[Set[str]] = None
    ) -> str:
        """Register a new adapter.
        
        Args:
            adapter_path: Path to adapter directory
            adapter_type: Type of adapter
            name: Adapter name
            tags: Optional tags
            
        Returns:
            Adapter ID
        """
        from datetime import datetime
        
        adapter_id = f"{adapter_type}_{name}"
        
        metadata = AdapterMetadata(
            adapter_id=adapter_id,
            adapter_type=adapter_type,
            name=name,
            version="1.0.0",
            path=adapter_path,
            dependencies=[],
            tags=tags or set(),
            created_at=datetime.utcnow().isoformat()
        )
        
        # Save metadata
        metadata_path = adapter_path / "adapter_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump({
                "adapter_id": metadata.adapter_id,
                "adapter_type": metadata.adapter_type,
                "name": metadata.name,
                "version": metadata.version,
                "path": str(metadata.path),
                "dependencies": metadata.dependencies,
                "tags": list(metadata.tags),
                "created_at": metadata.created_at
            }, f, indent=2)
        
        # Add to registry
        self.adapter_registry[adapter_id] = metadata
        logger.info(f"Registered adapter: {adapter_id}")
        
        return adapter_id
    
    def unload_adapter(self, adapter_id: str) -> None:
        """Unload an adapter from memory.
        
        Args:
            adapter_id: Adapter to unload
        """
        if adapter_id in self.loaded_adapters:
            del self.loaded_adapters[adapter_id]
            logger.info(f"Unloaded adapter: {adapter_id}")
    
    def clear_cache(self) -> None:
        """Clear all loaded adapters from cache."""
        self.loaded_adapters.clear()
        logger.info("Cleared adapter cache")


def main():
    """CLI entry point for adapter manager."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Adapter Manager")
    parser.add_argument("--base-model", required=True, help="Base model path")
    parser.add_argument("--adapters-dir", type=Path, required=True, help="Adapters directory")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # List adapters
    list_parser = subparsers.add_parser("list", help="List available adapters")
    list_parser.add_argument("--type", help="Filter by adapter type")
    
    # Register adapter
    register_parser = subparsers.add_parser("register", help="Register new adapter")
    register_parser.add_argument("--path", type=Path, required=True, help="Adapter path")
    register_parser.add_argument("--type", required=True, help="Adapter type")
    register_parser.add_argument("--name", required=True, help="Adapter name")
    register_parser.add_argument("--tags", nargs="*", help="Tags")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Initialize manager
    manager = AdapterManager(args.base_model, args.adapters_dir)
    
    if args.command == "list":
        print("\n=== Available Adapters ===")
        
        adapters = manager.adapter_registry.values()
        if args.type:
            adapters = [a for a in adapters if a.adapter_type == args.type]
        
        for adapter in adapters:
            print(f"\n{adapter.adapter_id}")
            print(f"  Type: {adapter.adapter_type}")
            print(f"  Name: {adapter.name}")
            print(f"  Version: {adapter.version}")
            print(f"  Path: {adapter.path}")
            print(f"  Tags: {', '.join(adapter.tags)}")
    
    elif args.command == "register":
        adapter_id = manager.register_adapter(
            args.path,
            args.type,
            args.name,
            set(args.tags) if args.tags else None
        )
        print(f"\nAdapter registered: {adapter_id}")


if __name__ == "__main__":
    main()
