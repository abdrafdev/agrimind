#!/usr/bin/env python3
"""
AgriMind Architecture Diagram Generator
Converts the architecture markdown description to a visual diagram
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import matplotlib.lines as mlines

def create_architecture_diagram():
    """Create and save architecture diagram"""
    
    # Create figure and axis
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Colors
    colors = {
        'data_sources': '#E8F4FD',
        'dal': '#FFF2CC', 
        'cache': '#E1D5E7',
        'agents': '#D5E8D4',
        'message_bus': '#FFE6CC',
        'ledger': '#F8CECC',
        'mode_controller': '#F0F0F0'
    }
    
    # Title
    ax.text(8, 11.5, 'AgriMind: Multi-Agent Farm Intelligence Architecture', 
            ha='center', va='center', fontsize=16, fontweight='bold')
    
    # Data Sources Layer (Top)
    data_box = FancyBboxPatch((1, 9), 14, 2, 
                              boxstyle="round,pad=0.1", 
                              facecolor=colors['data_sources'], 
                              edgecolor='black', linewidth=1)
    ax.add_patch(data_box)
    ax.text(8, 10.5, 'Data Sources Layer', ha='center', va='center', fontsize=12, fontweight='bold')
    
    # Sub-boxes for data sources
    ax.text(3, 10, 'Datasets\n(Primary)', ha='center', va='center', fontsize=10, fontweight='bold')
    ax.text(3, 9.5, '• sensor.json\n• weather.csv\n• resources.json\n• market.csv', ha='center', va='center', fontsize=8)
    
    ax.text(8, 10, 'External APIs\n(Secondary)', ha='center', va='center', fontsize=10, fontweight='bold')
    ax.text(8, 9.5, '• WeatherAPI\n• OpenWeather\n• AgroMonitoring\n• StormGlass', ha='center', va='center', fontsize=8)
    
    ax.text(13, 10, 'Mock Generators\n(Fallback)', ha='center', va='center', fontsize=10, fontweight='bold')
    ax.text(13, 9.5, '• Synthetic Sensor\n• Synthetic Weather\n• Synthetic Resources\n• Synthetic Market', ha='center', va='center', fontsize=8)
    
    # DAL and Cache Layer (Middle-Upper)
    dal_box = FancyBboxPatch((1, 7.5), 6.5, 1, 
                             boxstyle="round,pad=0.1", 
                             facecolor=colors['dal'], 
                             edgecolor='black', linewidth=1)
    ax.add_patch(dal_box)
    ax.text(4.25, 8, 'Data Access Layer\n(Priority: Dataset → API → Mock)', ha='center', va='center', fontsize=10, fontweight='bold')
    
    cache_box = FancyBboxPatch((8.5, 7.5), 6.5, 1, 
                               boxstyle="round,pad=0.1", 
                               facecolor=colors['cache'], 
                               edgecolor='black', linewidth=1)
    ax.add_patch(cache_box)
    ax.text(11.75, 8, 'Caching Layer\n(Read-Through + TTL)', ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Agents Layer (Middle)
    agents_box = FancyBboxPatch((1, 4.5), 14, 2.5, 
                                boxstyle="round,pad=0.1", 
                                facecolor=colors['agents'], 
                                edgecolor='black', linewidth=1)
    ax.add_patch(agents_box)
    ax.text(8, 6.5, 'Multi-Agent System', ha='center', va='center', fontsize=12, fontweight='bold')
    
    # Individual agents
    agent_positions = [
        (3, 5.8, 'Sensor\nAgents', '📊 Environmental\ndata collection'),
        (6, 5.8, 'Prediction\nAgents', '🔮 ML forecasts\n& analysis'),  
        (9, 5.8, 'Resource\nAgents', '🔄 Allocation &\nnegotiation'),
        (12, 5.8, 'Market\nAgents', '💰 Price tracking\n& trading')
    ]
    
    for x, y, title, desc in agent_positions:
        agent_box = FancyBboxPatch((x-0.75, y-0.5), 1.5, 1, 
                                   boxstyle="round,pad=0.05", 
                                   facecolor='white', 
                                   edgecolor='darkgreen', linewidth=1)
        ax.add_patch(agent_box)
        ax.text(x, y+0.2, title, ha='center', va='center', fontsize=9, fontweight='bold')
        ax.text(x, y-0.2, desc, ha='center', va='center', fontsize=7)
    
    # Message Bus (Middle-Lower)
    bus_box = FancyBboxPatch((3, 3), 10, 1, 
                             boxstyle="round,pad=0.1", 
                             facecolor=colors['message_bus'], 
                             edgecolor='black', linewidth=1)
    ax.add_patch(bus_box)
    ax.text(8, 3.5, 'Message Bus (Pub/Sub)\nTopics: sensor.data, predictions.out, resources.plan, market.prices, trade.*', 
            ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Bottom Layer
    ledger_box = FancyBboxPatch((1, 1), 6, 1.5, 
                                boxstyle="round,pad=0.1", 
                                facecolor=colors['ledger'], 
                                edgecolor='black', linewidth=1)
    ax.add_patch(ledger_box)
    ax.text(4, 1.75, 'Transaction Ledger\n(Agent-to-Agent Negotiations)', ha='center', va='center', fontsize=10, fontweight='bold')
    
    mode_box = FancyBboxPatch((9, 1), 6, 1.5, 
                              boxstyle="round,pad=0.1", 
                              facecolor=colors['mode_controller'], 
                              edgecolor='black', linewidth=1)
    ax.add_patch(mode_box)
    ax.text(12, 1.75, 'Mode/Health Controller\n(Normal ↔ Degraded Mode)', ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Arrows showing data flow
    # Data Sources → DAL/Cache
    ax.arrow(8, 8.8, 0, -0.2, head_width=0.2, head_length=0.1, fc='black', ec='black')
    
    # DAL/Cache → Agents  
    ax.arrow(4.25, 7.4, 0, -0.3, head_width=0.2, head_length=0.1, fc='black', ec='black')
    ax.arrow(11.75, 7.4, 0, -0.3, head_width=0.2, head_length=0.1, fc='black', ec='black')
    
    # Agents → Message Bus
    ax.arrow(8, 4.4, 0, -0.3, head_width=0.2, head_length=0.1, fc='black', ec='black')
    
    # Message Bus → Ledger/Mode Controller
    ax.arrow(6, 2.9, -1.5, -1.2, head_width=0.2, head_length=0.1, fc='black', ec='black')
    ax.arrow(10, 2.9, 1.5, -1.2, head_width=0.2, head_length=0.1, fc='black', ec='black')
    
    # Legend
    ax.text(0.5, 0.5, 'Priority Chain: Dataset → API → Mock\nModes: Hybrid | Offline | Degraded', 
            ha='left', va='bottom', fontsize=9, 
            bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgray'))
    
    # Save diagram
    plt.tight_layout()
    plt.savefig('architecture_diagram.png', dpi=300, bbox_inches='tight')
    plt.savefig('architecture_diagram.svg', format='svg', bbox_inches='tight')
    
    print("✅ Architecture diagrams saved:")
    print("   📊 architecture_diagram.png")
    print("   📊 architecture_diagram.svg")

if __name__ == "__main__":
    try:
        create_architecture_diagram()
    except ImportError as e:
        print("❌ Missing matplotlib dependency")
        print("   Install with: pip install matplotlib")
        print(f"   Error: {e}")
    except Exception as e:
        print(f"❌ Error generating diagram: {e}")