import networkx as nx

class OfflineNav:
    def __init__(self):
        print("[Maps] Loading Delhi Offline Network...")
        self.graph = nx.Graph()
        self._load_delhi_map()
        self.locations = sorted(list(self.graph.nodes))

    def _load_delhi_map(self):
        """
        Builds a graph of 20+ Major Delhi Landmarks with approx distances (km).
        """
        # --- 1. DEFINE NODES (LOCATIONS) ---
        nodes = [
            "Connaught Place", "India Gate", "Red Fort", "Chandni Chowk",
            "New Delhi Rly Station", "Kashmiri Gate", "Karol Bagh",
            "Dhaula Kuan", "IGI Airport", "Dwarka Sec 21", "Rohini East",
            "Pitampura", "Hauz Khas", "IIT Delhi", "Qutub Minar",
            "Nehru Place", "Lotus Temple", "Lajpat Nagar", "Akshardham",
            "Mayur Vihar", "Noida Sec 18", "Gurgaon Cyber City"
        ]
        self.graph.add_nodes_from(nodes)

        # --- 2. DEFINE EDGES (ROADS & DISTANCES) ---
        # Central Delhi Hub
        self.graph.add_edge("Connaught Place", "India Gate", weight=2.5)
        self.graph.add_edge("Connaught Place", "New Delhi Rly Station", weight=1.5)
        self.graph.add_edge("Connaught Place", "Karol Bagh", weight=4.0)
        self.graph.add_edge("Connaught Place", "Mandi House", weight=2.0) # Hidden node for connectivity

        # Old Delhi / North
        self.graph.add_edge("New Delhi Rly Station", "Chandni Chowk", weight=2.5)
        self.graph.add_edge("Chandni Chowk", "Red Fort", weight=1.2)
        self.graph.add_edge("Red Fort", "Kashmiri Gate", weight=3.0)
        self.graph.add_edge("Kashmiri Gate", "Rohini East", weight=12.0)
        self.graph.add_edge("Rohini East", "Pitampura", weight=4.0)
        
        # South Delhi
        self.graph.add_edge("India Gate", "Lajpat Nagar", weight=6.0)
        self.graph.add_edge("Lajpat Nagar", "Nehru Place", weight=4.5)
        self.graph.add_edge("Nehru Place", "Lotus Temple", weight=1.5)
        self.graph.add_edge("Nehru Place", "Hauz Khas", weight=5.5)
        self.graph.add_edge("Hauz Khas", "IIT Delhi", weight=2.0)
        self.graph.add_edge("IIT Delhi", "Qutub Minar", weight=3.0)
        
        # East Delhi / Noida Link
        self.graph.add_edge("India Gate", "Akshardham", weight=7.0)
        self.graph.add_edge("Akshardham", "Mayur Vihar", weight=3.5)
        self.graph.add_edge("Mayur Vihar", "Noida Sec 18", weight=5.0)

        # West / Airport Link
        self.graph.add_edge("Connaught Place", "Dhaula Kuan", weight=8.0)
        self.graph.add_edge("Karol Bagh", "Dhaula Kuan", weight=6.5)
        self.graph.add_edge("Dhaula Kuan", "IGI Airport", weight=9.0)
        self.graph.add_edge("IGI Airport", "Dwarka Sec 21", weight=6.0)
        self.graph.add_edge("IGI Airport", "Gurgaon Cyber City", weight=14.0)
        self.graph.add_edge("Dhaula Kuan", "Hauz Khas", weight=7.0) # Ring Road connection

    def get_directions(self, start_in, end_in):
        # 1. Fuzzy Search to match user input to real nodes
        start_node = self._fuzzy_match(start_in)
        end_node = self._fuzzy_match(end_in)

        if not start_node:
            return f"❌ Start location '{start_in}' not found.<br>Try: {', '.join(self.locations[:5])}..."
        if not end_node:
            return f"❌ End location '{end_in}' not found.<br>Try: {', '.join(self.locations[:5])}..."

        try:
            # 2. Authentic Dijkstra Algorithm
            path = nx.shortest_path(self.graph, source=start_node, target=end_node, weight='weight')
            total_dist = nx.shortest_path_length(self.graph, source=start_node, target=end_node, weight='weight')
            
            # 3. Format Output
            html = f"🗺️ <b>Route: {start_node} ➝ {end_node}</b><br>"
            html += f"<span class='text-xs text-slate-400'>Total Distance: {total_dist} km</span><br>"
            html += "<div class='mt-3 space-y-3'>"
            
            for i in range(len(path) - 1):
                curr = path[i]
                nxt = path[i+1]
                dist = self.graph[curr][nxt]['weight']
                html += (
                    f"<div class='flex items-center gap-3 bg-slate-800 p-2 rounded'>"
                    f"<span class='text-slate-400'>⬇</span>"
                    f"<div>"
                    f"<p class='text-sm font-bold text-white'>Go to {nxt}</p>"
                    f"<p class='text-xs text-slate-400'>Distance: {dist} km</p>"
                    f"</div></div>"
                )
            
            html += "<div class='flex gap-2 mt-2 text-green-400 font-bold'>📍 Arrived at Destination</div></div>"
            return html

        except nx.NetworkXNoPath:
            return "❌ No road connection found between these points."

    def _fuzzy_match(self, user_input):
        """
        Simple helper to find 'Hauz Khas' if user types 'hauz khas' or 'Hauz'.
        """
        user_input = user_input.lower().strip()
        for node in self.graph.nodes:
            if user_input in node.lower():
                return node
        return None

# --- Test Block ---
if __name__ == "__main__":
    nav = OfflineNav()
    # Test a complex route
    print(nav.get_directions("red fort", "airport"))