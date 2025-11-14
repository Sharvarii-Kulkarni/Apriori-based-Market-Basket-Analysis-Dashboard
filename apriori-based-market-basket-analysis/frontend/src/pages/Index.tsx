import { useState } from "react";
import { Header } from "@/components/dashboard/Header";
import { ParametersSection } from "@/components/dashboard/ParametersSection";
import { MetaCards } from "@/components/dashboard/MetaCards";
import { FrequentItemsets } from "@/components/dashboard/FrequentItemsets";
import { AssociationRules } from "@/components/dashboard/AssociationRules";
import { KeyInsights } from "@/components/dashboard/KeyInsights";
import { toast } from "@/hooks/use-toast";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export interface MetaData {
  file_name: string;
  n_transactions: number;
  n_items: number;
}

const Index = () => {
  const [minSupport, setMinSupport] = useState(0.01);
  const [minConfidence, setMinConfidence] = useState(0.001);
  const [metaData, setMetaData] = useState<MetaData | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleAnalyze = async (file: File) => {
    const form = new FormData();
    form.append("file", file);
    form.append("min_support", minSupport.toString());
    form.append("min_confidence", minConfidence.toString());

    try {
      const res = await fetch(`${API}/upload`, {
        method: "POST",
        body: form,
      });

      if (!res.ok) {
        const errorText = await res.text();
        try {
          const errorJson = JSON.parse(errorText);
          toast({
            title: "Upload Failed",
            description: errorJson.detail || errorText,
            variant: "destructive",
          });
        } catch {
          toast({
            title: "Upload Failed",
            description: errorText,
            variant: "destructive",
          });
        }
        return;
      }

      const responseData = await res.json();
      setMetaData({
        file_name: responseData.file_name || file.name,
        n_transactions: responseData.n_transactions,
        n_items: responseData.n_items,
      });
      
      setRefreshKey(prev => prev + 1);
      
      toast({
        title: "Analysis Complete",
        description: "Market basket analysis has been successfully completed!",
      });
    } catch (err) {
      console.error("Network error:", err);
      toast({
        title: "Network Error",
        description: err instanceof Error ? err.message : "Failed to connect to backend",
        variant: "destructive",
      });
    }
  };

  const handleSampleDataset = async (datasetId: string) => {
    try {
      const res = await fetch(`${API}/sample-dataset/${datasetId}`);
      if (!res.ok) {
        const errorText = await res.text();
        toast({
          title: "Failed to Load Sample",
          description: errorText,
          variant: "destructive",
        });
        return;
      }

      const responseData = await res.json();
      setMetaData({
        file_name: responseData.file_name,
        n_transactions: responseData.n_transactions,
        n_items: responseData.n_items,
      });

      setMinSupport(responseData.min_support);
      setMinConfidence(responseData.min_confidence);
      setRefreshKey(prev => prev + 1);

      toast({
        title: "Sample Dataset Loaded",
        description: `${responseData.file_name} loaded successfully!`,
      });
    } catch (err) {
      console.error("Error loading sample dataset:", err);
      toast({
        title: "Error",
        description: err instanceof Error ? err.message : "Failed to load sample dataset",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen py-8 px-4 md:px-8">
      <div className="max-w-7xl mx-auto space-y-6">
        <Header />
        
        <ParametersSection
          minSupport={minSupport}
          minConfidence={minConfidence}
          onMinSupportChange={setMinSupport}
          onMinConfidenceChange={setMinConfidence}
          onAnalyze={handleAnalyze}
          onSampleDataset={handleSampleDataset}
        />

        {metaData && (
          <>
            <MetaCards metaData={metaData} />
            <FrequentItemsets apiUrl={API} key={`fi-${refreshKey}`} />
            <AssociationRules apiUrl={API} key={`ar-${refreshKey}`} />
            <KeyInsights apiUrl={API} key={`ki-${refreshKey}`} />
          </>
        )}
      </div>
    </div>
  );
};

export default Index;
