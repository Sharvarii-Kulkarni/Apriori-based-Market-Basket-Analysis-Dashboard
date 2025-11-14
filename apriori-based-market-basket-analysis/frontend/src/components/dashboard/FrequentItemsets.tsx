import { useEffect, useRef, useState } from "react";
import { Layers } from "lucide-react";

interface FrequentItemsetsProps {
  apiUrl: string;
}

interface FrequentItemset {
  itemset: string[];
  support: number;
}

export const FrequentItemsets = ({ apiUrl }: FrequentItemsetsProps) => {
  const [itemsets, setItemsets] = useState<FrequentItemset[]>([]);
  const barChartRef = useRef<HTMLDivElement>(null);
  const wordCloudRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadData();
  }, [apiUrl]);

  const loadData = async () => {
    try {
      const res = await fetch(`${apiUrl}/frequent-itemsets`);
      if (!res.ok) return;
      const data = await res.json();
      setItemsets(data.frequent_itemsets || []);
      
      // Render visualizations
      if (data.frequent_itemsets && data.frequent_itemsets.length > 0) {
        renderBarChart(data.frequent_itemsets);
        renderWordCloud(data.frequent_itemsets);
      }
    } catch (err) {
      console.error("Error loading frequent itemsets:", err);
    }
  };

  const renderBarChart = (data: FrequentItemset[]) => {
    if (!barChartRef.current || !(window as any).Plotly) return;

    const top15 = data.slice(0, 15);
    const trace = {
      x: top15.map(d => d.support),
      y: top15.map(d => d.itemset.join(", ")),
      type: "bar",
      orientation: "h",
      marker: {
        color: "rgba(139, 92, 246, 0.8)",
        line: { color: "rgba(99, 102, 241, 1)", width: 2 }
      },
    };

    const layout = {
      title: { text: "Top 15 Itemsets by Support", font: { size: 16, color: "#6d28d9" } },
      xaxis: { title: "Support" },
      yaxis: { automargin: true },
      margin: { l: 150, r: 50, t: 50, b: 50 },
      height: 420,
    };

    (window as any).Plotly.newPlot(barChartRef.current, [trace], layout, { responsive: true });
  };

  const renderWordCloud = (data: FrequentItemset[]) => {
    if (!wordCloudRef.current || !(window as any).d3) return;

    const itemCounts: Record<string, number> = {};
    data.forEach(d => {
      d.itemset.forEach(item => {
        itemCounts[item] = (itemCounts[item] || 0) + d.support;
      });
    });

    const words = Object.entries(itemCounts).map(([text, size]) => ({
      text,
      size: Math.sqrt(size) * 100,
    }));

    const width = wordCloudRef.current.clientWidth;
    const height = 420;

    (window as any).d3.select(wordCloudRef.current).selectAll("*").remove();

    const layout = (window as any).d3.layout.cloud()
      .size([width, height])
      .words(words)
      .padding(5)
      .rotate(() => (Math.random() > 0.5 ? 0 : 90))
      .fontSize((d: any) => d.size)
      .on("end", (words: any) => {
        (window as any).d3.select(wordCloudRef.current)
          .append("svg")
          .attr("width", width)
          .attr("height", height)
          .append("g")
          .attr("transform", `translate(${width / 2},${height / 2})`)
          .selectAll("text")
          .data(words)
          .enter()
          .append("text")
          .style("font-size", (d: any) => `${d.size}px`)
          .style("fill", () => {
            const colors = ["#8b5cf6", "#6366f1", "#3b82f6", "#06b6d4"];
            return colors[Math.floor(Math.random() * colors.length)];
          })
          .style("font-weight", "600")
          .attr("text-anchor", "middle")
          .attr("transform", (d: any) => `translate(${d.x},${d.y})rotate(${d.rotate})`)
          .text((d: any) => d.text);
      });

    layout.start();
  };

  return (
    <div className="glass glass-hover rounded-2xl p-6 space-y-6 animate-fade-in">
      <div className="flex items-center gap-3 mb-4">
        <Layers className="w-6 h-6 text-primary" />
        <h2 className="text-2xl font-bold text-foreground">Frequent Itemsets</h2>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-card rounded-xl p-4 border border-border max-h-[420px] overflow-auto">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-muted">
              <tr className="border-b border-border">
                <th className="text-left p-3 font-semibold text-primary">Itemset</th>
                <th className="text-right p-3 font-semibold text-primary">Support</th>
              </tr>
            </thead>
            <tbody>
              {itemsets.slice(0, 20).map((item, idx) => (
                <tr key={idx} className="border-b border-border/50 hover:bg-muted/50 transition-colors">
                  <td className="p-3 text-foreground">{item.itemset.join(", ")}</td>
                  <td className="p-3 text-right font-mono text-muted-foreground">
                    {(item.support * 100).toFixed(2)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="bg-card rounded-xl p-4 border border-border">
          <div ref={barChartRef} className="w-full h-[420px]" />
        </div>
      </div>

      <div className="bg-card rounded-xl p-4 border border-border">
        <h3 className="text-lg font-semibold text-foreground mb-3">Word Cloud - Item Frequency</h3>
        <div ref={wordCloudRef} className="w-full h-[420px]" />
      </div>
    </div>
  );
};
