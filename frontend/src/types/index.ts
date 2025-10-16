export interface AllocationItem {
  retailer: string;
  placement: string;
  audience: string;
  sku: string;
  spend: number;
  expected_conversions: number;
  expected_revenue: number;
  expected_roas: number;
  is_experiment: boolean;
}

export interface Plan {
  objective: string;
  budget_total: number;
  budget_allocated: number;
  budget_experiment: number;
  constraints: Record<string, any>;
  allocation: AllocationItem[];
  experiments: Record<string, any>;
  rationale: string;
  adapters_used: string[];
  clean_room_mode: boolean;
  tool_calls: any[];
  expected_roas: number;
  expected_revenue: number;
  expected_margin?: number;
  created_at: string;
}

export interface ComparisonResult {
  comparison_id: string;
  plan_id?: string;
  clean_room_roas: number;
  clean_room_revenue: number;
  clean_room_accuracy: number;
  clean_room_skus: number;
  full_data_roas: number;
  full_data_revenue: number;
  full_data_accuracy: number;
  full_data_skus: number;
  roas_delta_pct: number;
  revenue_delta_pct: number;
  accuracy_delta_pct: number;
  sku_delta_pct: number;
  missing_capabilities: string[];
  blocked_fields: string[];
  created_at: string;
}

export interface Creative {
  sku: string;
  copy: string;
  policy_pass: boolean;
  reasons: string[];
  variants?: CreativeVariant[];
}

export interface CreativeVariant {
  text: string;
  compliant: boolean;
  violations: string[];
}

export interface AdapterMetadata {
  adapter_id: string;
  adapter_type: string;
  name: string;
  version: string;
  path: string;
  dependencies: string[];
  tags: string[];
  created_at: string;
  description: string;
  capabilities: string[];
  performance?: Record<string, number>;
}

export interface DemoResults {
  workflow_id: string;
  timestamp: string;
  steps: {
    harmonization: any;
    full_plan: Plan;
    clean_room_plan: Plan;
    comparison: ComparisonResult;
    creatives: {
      status: string;
      creatives: Creative[];
      adapters_used: string[];
      compliance_rate: number;
    };
    visualization: {
      layers: Array<{
        name: string;
        type: string;
        adapter_id?: string;
        model?: string;
        capabilities: string[];
      }>;
      composition_strategy: string;
      total_parameters: string;
      lora_parameters: string;
      composition_time_ms: number;
    };
  };
}

export interface WorkflowStep {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'error';
  icon: string;
}
