import { Activity } from "lucide-react";
import { Link } from "react-router-dom";

export const Header = () => {
  return (
    <header className="glass glass-hover rounded-2xl p-8 text-center animate-fade-in space-y-8">
      <div className="flex items-center justify-center gap-3 mb-3">
        <Link to="/learn" className="transition-transform hover:scale-110 -m1 - 8">
          <Activity className="w-10 h-10 text-primary animate-glow cursor-pointer" />
        </Link>
        <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent leading-snug">
         Market Basket Insights Dashboard
        </h1>
      </div>
      <div className="flex items-center justify-center gap-2 flex-wrap mt-2">
        <span className="px-4 py-1.5 rounded-full bg-primary/10 text-primary text-sm font-semibold border border-primary/20">
          Apriori
        </span>
        <span className="text-muted-foreground">•</span>
        <span className="px-4 py-1.5 rounded-full bg-accent/10 text-accent text-sm font-semibold border border-accent/20">
          Association Rules
        </span>
        <span className="text-muted-foreground">•</span>
        <span className="px-4 py-1.5 rounded-full bg-primary/10 text-primary text-sm font-semibold border border-primary/20">
          Interactive Visuals
        </span>
      </div>
    </header>
  );
};
