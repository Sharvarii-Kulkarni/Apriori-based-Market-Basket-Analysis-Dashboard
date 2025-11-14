import { Database, FileText, Package } from "lucide-react";
import { MetaData } from "@/pages/Index";

interface MetaCardsProps {
  metaData: MetaData;
}

export const MetaCards = ({ metaData }: MetaCardsProps) => {
  return (
    <div className="grid md:grid-cols-3 gap-4 animate-fade-in">
      <div className="glass glass-hover rounded-xl p-6 border-l-4 border-primary">
        <div className="flex items-center gap-3 mb-2">
          <FileText className="w-5 h-5 text-primary" />
          <span className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
            Dataset
          </span>
        </div>
        <p className="text-xl font-bold text-foreground">{metaData.file_name}</p>
      </div>

      <div className="glass glass-hover rounded-xl p-6 border-l-4 border-accent">
        <div className="flex items-center gap-3 mb-2">
          <Database className="w-5 h-5 text-accent" />
          <span className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
            Transactions
          </span>
        </div>
        <p className="text-xl font-bold text-foreground">{metaData.n_transactions.toLocaleString()}</p>
      </div>

      <div className="glass glass-hover rounded-xl p-6 border-l-4 border-primary">
        <div className="flex items-center gap-3 mb-2">
          <Package className="w-5 h-5 text-primary" />
          <span className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
            Unique Items
          </span>
        </div>
        <p className="text-xl font-bold text-foreground">{metaData.n_items.toLocaleString()}</p>
      </div>
    </div>
  );
};
