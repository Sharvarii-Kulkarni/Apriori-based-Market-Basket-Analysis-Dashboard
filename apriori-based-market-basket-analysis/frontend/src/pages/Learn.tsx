import { ArrowLeft, BookOpen, TrendingUp, Network, ShoppingCart, Lightbulb } from "lucide-react";
import { Link } from "react-router-dom";
import { Card } from "@/components/ui/card";

const Learn = () => {
  return (
    <div className="min-h-screen py-8 px-4 md:px-8">
      <div className="max-w-5xl mx-auto space-y-8">
        <div className="flex items-center gap-4 mb-6">
          <Link 
            to="/" 
            className="glass glass-hover rounded-xl p-3 inline-flex items-center gap-2 text-primary hover:text-primary-glow transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span className="font-medium">Back to Dashboard</span>
          </Link>
        </div>

        <header className="glass glass-hover rounded-2xl p-8 text-center animate-fade-in">
          <div className="flex items-center justify-center gap-3 mb-3">
            <BookOpen className="w-10 h-10 text-primary animate-glow" />
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-primary via-accent to-tertiary bg-clip-text text-transparent">
              Market Basket Analysis Guide
            </h1>
          </div>
          <p className="text-muted-foreground text-lg mt-2">
            Learn the fundamentals of MBA, Apriori algorithm, and Association Rules
          </p>
        </header>

        <div className="space-y-6">
          <Card className="glass glass-hover rounded-2xl p-8 animate-fade-in">
            <div className="flex items-start gap-4 mb-4">
              <div className="p-3 rounded-xl bg-primary/10 text-primary">
                <ShoppingCart className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-foreground mb-2">What is Market Basket Analysis?</h2>
                <p className="text-muted-foreground leading-relaxed">
                  Market Basket Analysis (MBA) is a data mining technique used to discover patterns in customer purchase behavior. 
                  It analyzes transactions to identify which products are frequently bought together, helping businesses understand 
                  customer preferences and optimize product placement, promotions, and recommendations.
                </p>
                <p className="text-muted-foreground leading-relaxed mt-3">
                  The name comes from analyzing the "basket" of items customers purchase together during shopping trips. By understanding 
                  these patterns, retailers can make data-driven decisions to increase sales and improve customer experience.
                </p>
              </div>
            </div>
          </Card>

          <Card className="glass glass-hover rounded-2xl p-8 animate-fade-in">
            <div className="flex items-start gap-4 mb-4">
              <div className="p-3 rounded-xl bg-accent/10 text-accent">
                <TrendingUp className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-foreground mb-2">The Apriori Algorithm</h2>
                <p className="text-muted-foreground leading-relaxed">
                  The Apriori algorithm is the most widely used method for mining frequent itemsets and generating association rules. 
                  It works on the principle that if an itemset is frequent, then all of its subsets must also be frequent. This property 
                  (called the "Apriori property") helps reduce the search space significantly.
                </p>
                <div className="mt-4 space-y-2">
                  <h3 className="font-semibold text-foreground">How it works:</h3>
                  <ol className="list-decimal list-inside space-y-2 text-muted-foreground">
                    <li><strong>Generate frequent itemsets:</strong> Find all combinations of items that appear together more frequently than the minimum support threshold</li>
                    <li><strong>Generate association rules:</strong> From frequent itemsets, create rules that meet the minimum confidence threshold</li>
                    <li><strong>Prune candidates:</strong> Use the Apriori property to eliminate itemsets that cannot be frequent</li>
                  </ol>
                </div>
                <div className="mt-4 p-4 rounded-lg bg-secondary/50 border border-border">
                  <p className="text-sm text-muted-foreground">
                    <strong>Support:</strong> How often an itemset appears in transactions<br/>
                    <strong>Confidence:</strong> How likely item B is purchased when item A is purchased
                  </p>
                </div>
              </div>
            </div>
          </Card>

          <Card className="glass glass-hover rounded-2xl p-8 animate-fade-in">
            <div className="flex items-start gap-4 mb-4">
              <div className="p-3 rounded-xl bg-tertiary/10 text-tertiary">
                <Network className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-foreground mb-2">Association Rules</h2>
                <p className="text-muted-foreground leading-relaxed">
                  Association rules represent relationships between items in the form "If A, then B" (A → B). These rules help identify 
                  which items are likely to be purchased together, enabling targeted cross-selling and upselling strategies.
                </p>
                <div className="mt-4 space-y-3">
                  <h3 className="font-semibold text-foreground">Key Metrics:</h3>
                  <div className="space-y-3">
                    <div className="p-4 rounded-lg bg-primary/5 border border-primary/20">
                      <p className="font-semibold text-primary mb-1">Support</p>
                      <p className="text-sm text-muted-foreground">
                        Measures how frequently the itemset appears in the dataset. Higher support indicates more common patterns.
                      </p>
                    </div>
                    <div className="p-4 rounded-lg bg-accent/5 border border-accent/20">
                      <p className="font-semibold text-accent mb-1">Confidence</p>
                      <p className="text-sm text-muted-foreground">
                        Measures the reliability of the rule. High confidence means the rule is strong and reliable.
                      </p>
                    </div>
                    <div className="p-4 rounded-lg bg-tertiary/5 border border-tertiary/20">
                      <p className="font-semibold text-tertiary mb-1">Lift</p>
                      <p className="text-sm text-muted-foreground">
                        Measures how much more likely items are purchased together compared to random chance. Lift &gt; 1 indicates positive correlation.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Card>

          <Card className="glass glass-hover rounded-2xl p-8 animate-fade-in">
            <div className="flex items-start gap-4 mb-4">
              <div className="p-3 rounded-xl bg-primary/10 text-primary">
                <Lightbulb className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-foreground mb-2">Why is Market Basket Analysis Important?</h2>
                <div className="space-y-3 text-muted-foreground">
                  <div className="flex gap-3">
                    <span className="text-accent font-bold">•</span>
                    <div>
                      <strong className="text-foreground">Product Placement:</strong> Place related products near each other to increase impulse purchases
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-accent font-bold">•</span>
                    <div>
                      <strong className="text-foreground">Promotional Strategies:</strong> Create bundle offers and combo deals based on frequently co-purchased items
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-accent font-bold">•</span>
                    <div>
                      <strong className="text-foreground">Inventory Management:</strong> Optimize stock levels based on item relationships
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-accent font-bold">•</span>
                    <div>
                      <strong className="text-foreground">Personalized Recommendations:</strong> Suggest products customers are likely to purchase
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-accent font-bold">•</span>
                    <div>
                      <strong className="text-foreground">Customer Understanding:</strong> Gain insights into shopping behaviors and preferences
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Card>

          <Card className="glass glass-hover rounded-2xl p-8 animate-fade-in">
            <h2 className="text-2xl font-bold text-foreground mb-4">Real-Life Applications</h2>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="p-4 rounded-lg bg-gradient-to-br from-primary/10 to-primary/5 border border-primary/20">
                <h3 className="font-semibold text-primary mb-2">🛒 Retail & E-commerce</h3>
                <p className="text-sm text-muted-foreground">
                  Amazon's "Customers who bought this also bought" feature uses MBA to drive additional sales through intelligent product recommendations.
                </p>
              </div>
              <div className="p-4 rounded-lg bg-gradient-to-br from-accent/10 to-accent/5 border border-accent/20">
                <h3 className="font-semibold text-accent mb-2">🍔 Fast Food Chains</h3>
                <p className="text-sm text-muted-foreground">
                  McDonald's uses MBA to design value meals and combo offers based on items frequently ordered together.
                </p>
              </div>
              <div className="p-4 rounded-lg bg-gradient-to-br from-tertiary/10 to-tertiary/5 border border-tertiary/20">
                <h3 className="font-semibold text-tertiary mb-2">💊 Healthcare</h3>
                <p className="text-sm text-muted-foreground">
                  Analyzing prescription patterns to identify drug interactions and improve treatment protocols.
                </p>
              </div>
              <div className="p-4 rounded-lg bg-gradient-to-br from-primary/10 to-accent/5 border border-border">
                <h3 className="font-semibold text-foreground mb-2">📚 Libraries & Streaming</h3>
                <p className="text-sm text-muted-foreground">
                  Netflix and Spotify use similar techniques to recommend content based on viewing/listening patterns.
                </p>
              </div>
              <div className="p-4 rounded-lg bg-gradient-to-br from-accent/10 to-tertiary/5 border border-border">
                <h3 className="font-semibold text-foreground mb-2">🏦 Banking & Finance</h3>
                <p className="text-sm text-muted-foreground">
                  Banks analyze transaction patterns to offer personalized financial products and detect fraudulent activities.
                </p>
              </div>
              <div className="p-4 rounded-lg bg-gradient-to-br from-tertiary/10 to-primary/5 border border-border">
                <h3 className="font-semibold text-foreground mb-2">📱 Telecommunications</h3>
                <p className="text-sm text-muted-foreground">
                  Telecom companies use MBA to create bundled service packages (internet + TV + phone) based on customer preferences.
                </p>
              </div>
            </div>
          </Card>

          <div className="text-center pt-4">
            <Link 
              to="/" 
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-primary to-accent text-white font-semibold hover:shadow-glow transition-all"
            >
              Try Market Basket Analysis
              <ArrowLeft className="w-5 h-5 rotate-180" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Learn;
