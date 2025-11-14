import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Play, Upload } from "lucide-react";

interface ParametersSectionProps {
  minSupport: number;
  minConfidence: number;
  onMinSupportChange: (value: number) => void;
  onMinConfidenceChange: (value: number) => void;
  onAnalyze: (file: File) => void;
  onSampleDataset: (datasetId: string) => void;
}

export const ParametersSection = ({
  minSupport,
  minConfidence,
  onMinSupportChange,
  onMinConfidenceChange,
  onAnalyze,
  onSampleDataset,
}: ParametersSectionProps) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleRunAnalysis = () => {
    if (!selectedFile) {
      alert("Please select a CSV file.");
      return;
    }
    onAnalyze(selectedFile);
  };

  return (
    <div className="glass glass-hover rounded-2xl p-6 space-y-6 animate-fade-in">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-foreground mb-2">Configure Analysis Parameters</h2>
        <p className="text-muted-foreground">Set thresholds and select your dataset to begin</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Min Support */}
        <div className="space-y-3">
          <Label htmlFor="min-support" className="text-base font-semibold text-primary">
            Minimum Support
          </Label>
          <div className="space-y-2">
            <input
            id="min-support"
            type="number"
            min={0.001}
            max={1}
            step={0.001}
            value={minSupport}
            onChange={(e) => onMinSupportChange(parseFloat(e.target.value))}
            className="w-full border border-input rounded-lg px-3 py-2 text-sm bg-card"
          />

          </div>
        </div>

        {/* Min Confidence */}
        <div className="space-y-3">
          <Label htmlFor="min-confidence" className="text-base font-semibold text-accent">
            Minimum Confidence
          </Label>
          <div className="space-y-2">
            <input
  id="min-confidence"
  type="number"
  min={0.001}
  max={1}
  step={0.001}
  value={minConfidence}
  onChange={(e) => onMinConfidenceChange(parseFloat(e.target.value))}
  className="w-full border border-input rounded-lg px-3 py-2 text-sm bg-card"
/>
          </div>
        </div>
      </div>

      <div className="border-t border-border pt-6 space-y-4">
        <div className="space-y-3">
          <Label htmlFor="sample-dataset" className="text-base font-semibold">
            Select Sample Dataset
          </Label>
          <Select onValueChange={onSampleDataset}>
            <SelectTrigger id="sample-dataset" className="w-full bg-card">
              <SelectValue placeholder="Choose a sample dataset..." />
            </SelectTrigger>
            <SelectContent className="bg-popover z-50">
              <SelectItem value="groceries">🛒 Grocery Store Dataset</SelectItem>
              <SelectItem value="electronics">💻 Electronics Store Dataset</SelectItem>
              <SelectItem value="office">📎 Office Supplies Dataset</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center gap-3">
          <div className="h-px flex-1 bg-border" />
          <span className="text-sm text-muted-foreground font-medium">OR</span>
          <div className="h-px flex-1 bg-border" />
        </div>

        <div className="space-y-3">
          <Label htmlFor="csv-file" className="text-base font-semibold">
            Upload Your CSV File
          </Label>
          <div className="flex gap-3">
            <div className="flex-1">
              <input
                id="csv-file"
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="w-full px-4 py-2.5 rounded-lg border border-input bg-card text-sm file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-primary-foreground hover:file:bg-primary/90 transition-colors"
              />
            </div>
            <Button
              onClick={handleRunAnalysis}
              size="lg"
              className="gradient-primary hover:opacity-90 transition-opacity font-semibold px-8 shadow-lg"
            >
              <Play className="w-4 h-4 mr-2" />
              Run Analysis
            </Button>
          </div>
          {selectedFile && (
            <p className="text-sm text-muted-foreground flex items-center gap-2">
              <Upload className="w-4 h-4" />
              Selected: <span className="font-medium text-foreground">{selectedFile.name}</span>
            </p>
          )}
        </div>
      </div>
    </div>
  );
};
