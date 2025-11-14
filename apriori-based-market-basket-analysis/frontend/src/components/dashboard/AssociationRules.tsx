import { useEffect, useRef, useState } from "react";
import { GitBranch } from "lucide-react";

interface AssociationRulesProps {
  apiUrl: string;
}

interface Rule {
  antecedent: string[];
  consequent: string[];
  support: number;
  confidence: number;
  lift: number;
  n_transactions: number;
}

export const AssociationRules = ({ apiUrl }: AssociationRulesProps) => {
  const [rules, setRules] = useState<Rule[]>([]);
  const networkRef = useRef<HTMLDivElement>(null);
  const heatmapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadData();
  }, [apiUrl]);

  const loadData = async () => {
    try {
      const res = await fetch(`${apiUrl}/rules`);
      if (!res.ok) return;
      const data = await res.json();
      setRules(data.rules || []);
      
      if (data.rules && data.rules.length > 0) {
        renderNetwork(data.rules);
      }
      
      const heatmapRes = await fetch(`${apiUrl}/heatmap`);
      if (heatmapRes.ok) {
        const heatmapData = await heatmapRes.json();
        renderHeatmap(heatmapData);
      }
    } catch (err) {
      console.error("Error loading association rules:", err);
    }
  };

  const renderNetwork = (data: Rule[]) => {
    if (!networkRef.current || !(window as any).d3) return;

    const nodes: any[] = [];
    const links: any[] = [];
    const nodeMap = new Map();

    data.slice(0, 20).forEach((rule, idx) => {
      const antStr = rule.antecedent.join(", ");
      const consStr = rule.consequent.join(", ");

      if (!nodeMap.has(antStr)) {
        nodeMap.set(antStr, nodes.length);
        nodes.push({ id: antStr, group: 1 });
      }
      if (!nodeMap.has(consStr)) {
        nodeMap.set(consStr, nodes.length);
        nodes.push({ id: consStr, group: 2 });
      }

      links.push({
        source: nodeMap.get(antStr),
        target: nodeMap.get(consStr),
        value: rule.confidence,
      });
    });

    const width = networkRef.current.clientWidth;
    const height = 420;

    (window as any).d3.select(networkRef.current).selectAll("*").remove();

    const svg = (window as any).d3.select(networkRef.current)
      .append("svg")
      .attr("width", width)
      .attr("height", height);

    const simulation = (window as any).d3.forceSimulation(nodes)
      .force("link", (window as any).d3.forceLink(links).id((d: any) => d.index).distance(80))
      .force("charge", (window as any).d3.forceManyBody().strength(-200))
      .force("center", (window as any).d3.forceCenter(width / 2, height / 2));

    const link = svg.append("g")
      .selectAll("line")
      .data(links)
      .enter()
      .append("line")
      .attr("stroke", "#94a3b8")
      .attr("stroke-width", 2)
      .attr("stroke-opacity", 0.6);

    const node = svg.append("g")
      .selectAll("circle")
      .data(nodes)
      .enter()
      .append("circle")
      .attr("r", 8)
      .attr("fill", (d: any) => (d.group === 1 ? "#8b5cf6" : "#3b82f6"))
      .call((window as any).d3.drag()
        .on("start", (event: any, d: any) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on("drag", (event: any, d: any) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on("end", (event: any, d: any) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }));

    const text = svg.append("g")
      .selectAll("text")
      .data(nodes)
      .enter()
      .append("text")
      .text((d: any) => d.id)
      .attr("font-size", "10px")
      .attr("fill", "#1e293b")
      .attr("font-weight", "600");

    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);

      node
        .attr("cx", (d: any) => d.x)
        .attr("cy", (d: any) => d.y);

      text
        .attr("x", (d: any) => d.x + 12)
        .attr("y", (d: any) => d.y + 4);
    });
  };

  const renderHeatmap = (data: any) => {
    if (!heatmapRef.current || !(window as any).Plotly) return;
    
    // Extract items and matrix from the data
    const items = data.items || [];
    const matrix = data.matrix || [];
    
    if (items.length === 0 || matrix.length === 0) return;
    
    const trace = {
      x: items,
      y: items,
      z: matrix,
      type: "heatmap",
      colorscale: "Viridis",
    };

    const layout = {
      title: { text: "Item Co-occurrence Heatmap", font: { size: 16, color: "#6d28d9" } },
      xaxis: { title: "Items" },
      yaxis: { title: "Items" },
      height: 420,
    };

    (window as any).Plotly.newPlot(heatmapRef.current, [trace], layout, { responsive: true });
  };

  return (
    <div className="glass glass-hover rounded-2xl p-6 space-y-6 animate-fade-in">
      <div className="flex items-center gap-3 mb-4">
        <GitBranch className="w-6 h-6 text-accent" />
        <h2 className="text-2xl font-bold text-foreground">Association Rules</h2>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-card rounded-xl p-4 border border-border max-h-[420px] overflow-auto">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-muted">
              <tr className="border-b border-border">
                <th className="text-left p-2 font-semibold text-primary">Antecedent</th>
                <th className="text-left p-2 font-semibold text-primary">Consequent</th>
                <th className="text-right p-2 font-semibold text-primary">Support</th>
                <th className="text-right p-2 font-semibold text-primary">Confidence</th>
                <th className="text-right p-2 font-semibold text-primary">Lift</th>
                <th className="text-right p-2 font-semibold text-primary">Txns</th>
              </tr>
            </thead>
            <tbody>
              {rules.slice(0, 30).map((rule, idx) => (
                <tr key={idx} className="border-b border-border/50 hover:bg-muted/50 transition-colors">
                  <td className="p-2 text-foreground">{rule.antecedent.join(", ")}</td>
                  <td className="p-2 text-foreground">{rule.consequent.join(", ")}</td>
                  <td className="p-2 text-right font-mono text-muted-foreground">
                    {(rule.support * 100).toFixed(2)}%
                  </td>
                  <td className="p-2 text-right font-mono text-muted-foreground">
                    {(rule.confidence * 100).toFixed(2)}%
                  </td>
                  <td className="p-2 text-right font-mono text-muted-foreground">
                    {rule.lift.toFixed(2)}
                  </td>
                  <td className="p-2 text-right font-mono text-muted-foreground">
                    {rule.n_transactions}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="bg-card rounded-xl p-4 border border-border">
          <h3 className="text-lg font-semibold text-foreground mb-3">Rule Network</h3>
          <div ref={networkRef} className="w-full h-[380px]" />
        </div>
      </div>

      <div className="bg-card rounded-xl p-4 border border-border">
        <div ref={heatmapRef} className="w-full h-[420px]" />
      </div>
    </div>
  );
};
