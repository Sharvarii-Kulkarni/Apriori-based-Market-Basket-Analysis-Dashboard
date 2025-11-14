import { useEffect, useState } from "react";
import { Lightbulb } from "lucide-react";

interface KeyInsightsProps {
  apiUrl: string;
}

export const KeyInsights = ({ apiUrl }: KeyInsightsProps) => {
  const [insights, setInsights] = useState<string[]>([]);

  useEffect(() => {
    loadData();
  }, [apiUrl]);

  const loadData = async () => {
    try {
      const res = await fetch(`${apiUrl}/insights`);
      if (!res.ok) return;
      const data = await res.json();
      setInsights(data.insights || []);
    } catch (err) {
      console.error("Error loading insights:", err);
    }
  };

  if (insights.length === 0) return null;

  return (
    <div className="glass glass-hover rounded-2xl p-6 space-y-4 animate-fade-in">
      <div className="flex items-center gap-3 mb-4">
        <Lightbulb className="w-6 h-6 text-accent" />
        <h2 className="text-2xl font-bold text-foreground">Key Insights</h2>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {insights.map((insight, idx) => (
          <div
            key={idx}
            className="bg-gradient-to-br from-primary/5 to-accent/5 rounded-xl p-5 border border-primary/20 hover:border-primary/40 transition-all hover:shadow-lg"
          >
            <p className="text-foreground leading-relaxed">{insight}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
