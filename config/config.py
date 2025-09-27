"""
AgriMind: Configuration Management
Centralized configuration system for all AgriMind agents and components.

Features:
- Environment-specific configurations
- API key management
- Agent-specific settings
- Degraded mode configurations
- Logging configuration
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class AgentConfig:
    """Configuration for a specific agent type"""
    agent_type: str
    enabled: bool
    initial_balance: float
    update_interval: int
    specific_config: Dict[str, Any]


@dataclass
class SystemConfig:
    """System-wide configuration"""
    environment: str
    region: str
    offline_mode: bool
    simulation_speed: float
    max_agents: int
    message_ttl_hours: int


class ConfigManager:
    """
    Centralized configuration manager for AgriMind system
    """
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "config/agrimind_config.yaml"
        self.config_data: Dict[str, Any] = {}
        self.api_keys: Dict[str, str] = {}
        
        # Load configuration
        self._load_configuration()
        self._load_api_keys()
    
    def _load_configuration(self):
        """Load configuration from YAML file"""
        config_path = Path(self.config_file)
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as file:
                    self.config_data = yaml.safe_load(file) or {}
                print(f"Loaded configuration from {config_path}")
            except Exception as e:
                print(f"Error loading config file: {e}")
                self.config_data = self._default_configuration()
        else:
            print(f"Config file {config_path} not found, using defaults")
            self.config_data = self._default_configuration()
            self._save_default_config()
    
    def _load_api_keys(self):
        """Load API keys from environment variables"""
        self.api_keys = {
            # Weather API providers (in order of preference)
            "weather_api_key": os.getenv("WEATHER_API_KEY", ""),           # WeatherAPI.com (primary)
            "openweather_api_key": os.getenv("OPENWEATHER_API_KEY", ""),   # OpenWeatherMap (backup)
            "stormglass_api_key": os.getenv("STORMGLASS_API_KEY", ""),     # StormGlass (backup)
            
            # Agricultural/Soil data providers
            "agro_api_key": os.getenv("AGRO_API_KEY", ""),                 # AgroMonitoring (satellite soil data)
            
            # Market data providers (future expansion)
            "market_api_key": os.getenv("MARKET_API_KEY", ""),             # Market data APIs
        }
        
        # Filter out empty keys
        self.api_keys = {k: v for k, v in self.api_keys.items() if v}
        
        if self.api_keys:
            print(f"Loaded {len(self.api_keys)} API keys from environment")
        else:
            print("No API keys found - using mock data only")
    
    def _default_configuration(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            "system": {
                "environment": "development",
                "region": "california_central_valley",
                "offline_mode": False,
                "simulation_speed": 1.0,
                "max_agents": 20,
                "message_ttl_hours": 24,
                "log_level": "INFO"
            },
            "agents": {
                "sensor": {
                    "enabled": True,
                    "initial_balance": 1000.0,
                    "update_interval": 300,  # 5 minutes
                    "sensors": {
                        "soil_moisture": {
                            "enabled": True,
                            "range": [0.1, 0.8],
                            "optimal": [0.3, 0.6]
                        },
                        "temperature": {
                            "enabled": True,
                            "range": [5, 45],
                            "optimal": [18, 28]
                        },
                        "humidity": {
                            "enabled": True,
                            "range": [30, 95],
                            "optimal": [40, 70]
                        },
                        "pest_detection": {
                            "enabled": True,
                            "confidence_threshold": 0.7
                        }
                    },
                    "pricing": {
                        "soil_moisture": 0.50,
                        "temperature": 0.30,
                        "humidity": 0.30,
                        "pest_detection": 1.00
                    }
                },
                "prediction": {
                    "enabled": True,
                    "initial_balance": 1500.0,
                    "update_interval": 1800,  # 30 minutes
                    "models": {
                        "irrigation_need": {
                            "enabled": True,
                            "confidence_threshold": 0.6,
                            "data_sources": ["soil_moisture", "temperature", "humidity"]
                        },
                        "weather_forecast": {
                            "enabled": True,
                            "forecast_hours": 24,
                            "confidence_threshold": 0.5
                        },
                        "pest_risk": {
                            "enabled": True,
                            "confidence_threshold": 0.7
                        },
                        "harvest_timing": {
                            "enabled": True,
                            "crop_cycle_days": 90
                        }
                    },
                    "pricing": {
                        "irrigation_need": 2.0,
                        "weather_forecast": 1.5,
                        "pest_risk": 3.0,
                        "harvest_timing": 5.0
                    }
                },
                "resource": {
                    "enabled": True,
                    "initial_balance": 5000.0,
                    "update_interval": 3600,  # 1 hour
                    "resources": {
                        "water": {
                            "total_capacity": 10000,
                            "peak_hours": [6, 18],
                            "efficiency_bonus": 0.15
                        },
                        "fertilizer": {
                            "inventory": {
                                "nitrogen": 500,
                                "phosphorus": 300,
                                "potassium": 400
                            },
                            "application_rate": 25
                        },
                        "equipment": {
                            "tractors": 2,
                            "irrigation_pumps": 4,
                            "sprayers": 3,
                            "harvesters": 1
                        },
                        "labor": {
                            "available_workers": 8,
                            "hourly_rates": {
                                "basic": 10,
                                "intermediate": 12,
                                "expert": 15
                            }
                        }
                    },
                    "pricing": {
                        "water": 0.05,      # per liter
                        "fertilizer": 2.50,  # per kg
                        "equipment": 15.0,   # per hour
                        "labor": 12.0       # per hour
                    }
                },
                "market": {
                    "enabled": True,
                    "initial_balance": 2000.0,
                    "update_interval": 300,  # 5 minutes
                    "crops": {
                        "tomatoes": {
                            "base_price": 3.50,
                            "volatility": 0.15,
                            "seasonality": 0.3
                        },
                        "corn": {
                            "base_price": 0.85,
                            "volatility": 0.10,
                            "seasonality": 0.2
                        },
                        "wheat": {
                            "base_price": 0.65,
                            "volatility": 0.08,
                            "seasonality": 0.15
                        }
                    },
                    "commission_rate": 0.03,
                    "quality_multipliers": {
                        "A": 1.2,
                        "B": 1.0,
                        "C": 0.8
                    }
                }
            },
            "farms": {
                "farm_1": {
                    "location": "fresno_ca",
                    "crop_type": "tomatoes",
                    "farm_size_acres": 50,
                    "coordinates": [36.7378, -119.7871]
                },
                "farm_2": {
                    "location": "modesto_ca",
                    "crop_type": "corn",
                    "farm_size_acres": 120,
                    "coordinates": [37.6391, -120.9969]
                },
                "farm_3": {
                    "location": "salinas_ca",
                    "crop_type": "lettuce",
                    "farm_size_acres": 80,
                    "coordinates": [36.6777, -121.6555]
                }
            },
            "degraded_mode": {
                "enabled": True,
                "cache_expiry_hours": 6,
                "fallback_data_age_limit_hours": 24,
                "offline_detection_timeout": 30,  # seconds
                "rule_based_confidence": 0.4
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file_logging": True,
                "log_directory": "logs",
                "max_log_size_mb": 100,
                "backup_count": 5,
                "transaction_logging": True
            },
            "simulation": {
                "demo_mode": True,
                "demo_duration_minutes": 10,
                "accelerated_time": False,
                "time_multiplier": 1.0,
                "network_failure_chance": 0.05,
                "api_failure_chance": 0.10
            }
        }
    
    def _save_default_config(self):
        """Save default configuration to file"""
        config_path = Path(self.config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_path, 'w') as file:
                yaml.dump(self.config_data, file, default_flow_style=False, indent=2)
            print(f"Saved default configuration to {config_path}")
        except Exception as e:
            print(f"Error saving default config: {e}")
    
    def get_system_config(self) -> SystemConfig:
        """Get system configuration"""
        system_data = self.config_data.get("system", {})
        
        return SystemConfig(
            environment=system_data.get("environment", "development"),
            region=system_data.get("region", "california_central_valley"),
            offline_mode=system_data.get("offline_mode", False),
            simulation_speed=system_data.get("simulation_speed", 1.0),
            max_agents=system_data.get("max_agents", 20),
            message_ttl_hours=system_data.get("message_ttl_hours", 24)
        )
    
    def get_agent_config(self, agent_type: str) -> AgentConfig:
        """Get configuration for a specific agent type"""
        agents_data = self.config_data.get("agents", {})
        agent_data = agents_data.get(agent_type, {})
        
        if not agent_data:
            raise ValueError(f"No configuration found for agent type: {agent_type}")
        
        return AgentConfig(
            agent_type=agent_type,
            enabled=agent_data.get("enabled", True),
            initial_balance=agent_data.get("initial_balance", 1000.0),
            update_interval=agent_data.get("update_interval", 3600),
            specific_config=agent_data
        )
    
    def get_farm_config(self, farm_id: str) -> Dict[str, Any]:
        """Get configuration for a specific farm"""
        farms_data = self.config_data.get("farms", {})
        return farms_data.get(farm_id, {})
    
    def get_all_farms(self) -> Dict[str, Dict[str, Any]]:
        """Get all farm configurations"""
        return self.config_data.get("farms", {})
    
    def get_api_keys(self) -> Dict[str, str]:
        """Get API keys"""
        return self.api_keys.copy()
    
    def get_degraded_mode_config(self) -> Dict[str, Any]:
        """Get degraded mode configuration"""
        return self.config_data.get("degraded_mode", {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return self.config_data.get("logging", {})
    
    def get_simulation_config(self) -> Dict[str, Any]:
        """Get simulation configuration"""
        return self.config_data.get("simulation", {})
    
    def is_agent_enabled(self, agent_type: str) -> bool:
        """Check if an agent type is enabled"""
        agents_data = self.config_data.get("agents", {})
        agent_data = agents_data.get(agent_type, {})
        return agent_data.get("enabled", False)
    
    def get_config(self, path: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated path"""
        keys = path.split('.')
        current = self.config_data
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def set_config(self, path: str, value: Any):
        """Set configuration value by dot-separated path"""
        keys = path.split('.')
        current = self.config_data
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the value
        current[keys[-1]] = value
    
    def save_config(self):
        """Save current configuration to file"""
        config_path = Path(self.config_file)
        
        try:
            with open(config_path, 'w') as file:
                yaml.dump(self.config_data, file, default_flow_style=False, indent=2)
            print(f"Configuration saved to {config_path}")
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Check system config
        system_config = self.config_data.get("system", {})
        if not system_config.get("region"):
            issues.append("System region not configured")
        
        # Check agent configs
        agents_config = self.config_data.get("agents", {})
        required_agents = ["sensor", "prediction", "resource", "market"]
        
        for agent_type in required_agents:
            if agent_type not in agents_config:
                issues.append(f"Missing configuration for {agent_type} agent")
            elif not isinstance(agents_config[agent_type].get("initial_balance"), (int, float)):
                issues.append(f"Invalid initial_balance for {agent_type} agent")
        
        # Check farm configs
        farms_config = self.config_data.get("farms", {})
        if not farms_config:
            issues.append("No farms configured")
        
        for farm_id, farm_config in farms_config.items():
            if not farm_config.get("location"):
                issues.append(f"Farm {farm_id} missing location")
            if not farm_config.get("crop_type"):
                issues.append(f"Farm {farm_id} missing crop_type")
        
        return issues


# Global configuration manager instance
config_manager = ConfigManager()


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance"""
    return config_manager


# Environment-specific configuration files
def get_environment_config_file() -> str:
    """Get environment-specific configuration file"""
    env = os.getenv("AGRIMIND_ENV", "development")
    return f"config/agrimind_{env}.yaml"


# Utility functions for common configuration access
def get_agent_config(agent_type: str) -> AgentConfig:
    """Utility function to get agent configuration"""
    return config_manager.get_agent_config(agent_type)


def get_api_keys() -> Dict[str, str]:
    """Utility function to get API keys"""
    return config_manager.get_api_keys()


def is_degraded_mode_enabled() -> bool:
    """Check if degraded mode is enabled"""
    return config_manager.get_config("degraded_mode.enabled", True)


def get_log_level() -> str:
    """Get logging level"""
    return config_manager.get_config("logging.level", "INFO")


def is_demo_mode() -> bool:
    """Check if running in demo mode"""
    return config_manager.get_config("simulation.demo_mode", True)


# Configuration validation
def validate_environment():
    """Validate the current configuration environment"""
    issues = config_manager.validate_config()
    
    if issues:
        print("⚠️  Configuration Issues Found:")
        for issue in issues:
            print(f"  - {issue}")
        print("\nPlease check your configuration file and environment variables.")
        return False
    else:
        print("✅ Configuration validation passed")
        return True


if __name__ == "__main__":
    # Run configuration validation when executed directly
    print("AgriMind Configuration Manager")
    print("=" * 40)
    
    # Show current configuration summary
    system_config = config_manager.get_system_config()
    print(f"Environment: {system_config.environment}")
    print(f"Region: {system_config.region}")
    print(f"Offline Mode: {system_config.offline_mode}")
    
    # Show enabled agents
    print("\nEnabled Agents:")
    for agent_type in ["sensor", "prediction", "resource", "market"]:
        if config_manager.is_agent_enabled(agent_type):
            print(f"  ✅ {agent_type.title()} Agent")
        else:
            print(f"  ❌ {agent_type.title()} Agent (disabled)")
    
    # Show API keys status
    api_keys = config_manager.get_api_keys()
    print(f"\nAPI Keys: {len(api_keys)} configured")
    for key_name in api_keys:
        print(f"  🔑 {key_name}")
    
    # Validate configuration
    print("\nValidation:")
    validate_environment()