import { motion } from 'framer-motion';
import { Brain, Building, Factory, Zap, ArrowDown, Info } from 'lucide-react';
import { useState } from 'react';

interface FederationGraphProps {
  activeAdapters: string[];
  compositionData?: {
    total_parameters: string;
    lora_parameters: string;
    composition_time_ms: number;
    composition_strategy: string;
  };
}

const adapterNodes = [
  {
    id: 'generic',
    label: 'Generic LLM',
    sublabel: 'Llama 3.1 8B',
    icon: Brain,
    color: 'from-blue-500 to-blue-600',
    borderColor: 'border-blue-400',
    bgColor: 'bg-blue-50',
    capabilities: ['General reasoning', 'Tool use', 'Schema comprehension'],
  },
  {
    id: 'industry',
    label: 'Industry LoRA',
    sublabel: 'Retail Media',
    icon: Building,
    color: 'from-purple-500 to-purple-600',
    borderColor: 'border-purple-400',
    bgColor: 'bg-purple-50',
    capabilities: ['RMIS schema', 'Clean room protocols', 'Campaign metrics'],
  },
  {
    id: 'manufacturer',
    label: 'Manufacturer LoRA',
    sublabel: 'Brand X',
    icon: Factory,
    color: 'from-amber-500 to-amber-600',
    borderColor: 'border-amber-400',
    bgColor: 'bg-amber-50',
    capabilities: ['Brand tone', 'Product hierarchies', 'Private metrics'],
  },
  {
    id: 'task',
    label: 'Task LoRA',
    sublabel: 'Planning',
    icon: Zap,
    color: 'from-green-500 to-green-600',
    borderColor: 'border-green-400',
    bgColor: 'bg-green-50',
    capabilities: ['Budget allocation', 'Tool calling', 'Constraints'],
  },
];

export default function FederationGraph({ activeAdapters, compositionData }: FederationGraphProps) {
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);

  return (
    <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl shadow-2xl p-8 text-white">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-2xl font-bold mb-1">🔗 Federated LLM Stack</h2>
          <p className="text-slate-400 text-sm">
            Dynamic adapter composition for superior performance
          </p>
        </div>
        <div className="flex items-center gap-2 bg-slate-800/50 px-4 py-2 rounded-lg">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          <span className="text-sm text-slate-300">Active</span>
        </div>
      </div>

      {/* Adapter Nodes */}
      <div className="flex flex-col items-center space-y-4 mb-8">
        {adapterNodes.map((node, index) => {
          const isActive = activeAdapters.includes(node.id);
          const Icon = node.icon;

          return (
            <div key={node.id} className="w-full flex flex-col items-center">
              <motion.div
                className={`
                  relative w-full max-w-md p-6 rounded-xl border-2 transition-all duration-300
                  ${isActive ? `${node.borderColor} ${node.bgColor} shadow-lg` : 'border-slate-700 bg-slate-800/30'}
                  ${hoveredNode === node.id ? 'scale-105' : ''}
                `}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                onMouseEnter={() => setHoveredNode(node.id)}
                onMouseLeave={() => setHoveredNode(null)}
              >
                {/* Status Indicator */}
                {isActive && (
                  <motion.div
                    className="absolute -top-2 -right-2 bg-green-500 text-white text-xs px-2 py-1 rounded-full font-semibold shadow-lg"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: index * 0.1 + 0.2 }}
                  >
                    ✓ Active
                  </motion.div>
                )}

                <div className="flex items-start gap-4">
                  {/* Icon */}
                  <div className={`
                    p-3 rounded-lg bg-gradient-to-br ${node.color} text-white
                    ${isActive ? 'shadow-lg' : 'opacity-50'}
                  `}>
                    <Icon className="w-6 h-6" />
                  </div>

                  {/* Content */}
                  <div className="flex-1">
                    <h3 className={`font-bold text-lg ${isActive ? 'text-slate-900' : 'text-white'}`}>
                      {node.label}
                    </h3>
                    <p className={`text-sm mb-3 ${isActive ? 'text-slate-600' : 'text-slate-400'}`}>
                      {node.sublabel}
                    </p>

                    {/* Capabilities */}
                    {(isActive || hoveredNode === node.id) && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        className="space-y-1"
                      >
                        {node.capabilities.map((cap, i) => (
                          <div key={i} className="flex items-center gap-2">
                            <div className={`w-1.5 h-1.5 rounded-full ${isActive ? 'bg-slate-600' : 'bg-slate-500'}`}></div>
                            <span className={`text-xs ${isActive ? 'text-slate-700' : 'text-slate-400'}`}>
                              {cap}
                            </span>
                          </div>
                        ))}
                      </motion.div>
                    )}
                  </div>
                </div>
              </motion.div>

              {/* Arrow */}
              {index < adapterNodes.length - 1 && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: isActive ? 1 : 0.3 }}
                  transition={{ delay: index * 0.1 + 0.15 }}
                  className="my-2"
                >
                  <ArrowDown className={`w-6 h-6 ${isActive ? 'text-green-400' : 'text-slate-600'}`} />
                </motion.div>
              )}
            </div>
          );
        })}
      </div>

      {/* Composition Metrics */}
      {compositionData && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-6 border-t border-slate-700"
        >
          <MetricCard
            label="Total Parameters"
            value={compositionData.total_parameters}
            icon="📊"
          />
          <MetricCard
            label="LoRA Parameters"
            value={compositionData.lora_parameters}
            icon="⚡"
          />
          <MetricCard
            label="Composition Time"
            value={`${compositionData.composition_time_ms}ms`}
            icon="⏱️"
          />
          <MetricCard
            label="Strategy"
            value={compositionData.composition_strategy}
            icon="🎯"
          />
        </motion.div>
      )}

      {/* Info Box */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="mt-6 bg-blue-500/10 border border-blue-500/30 rounded-lg p-4 flex items-start gap-3"
      >
        <Info className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-slate-300">
          <strong className="text-white">How it works:</strong> Each adapter layer adds specialized knowledge.
          The generic LLM provides base reasoning, industry adapter adds retail media expertise,
          manufacturer adapter contributes private data access, and task adapter optimizes for specific operations.
        </div>
      </motion.div>
    </div>
  );
}

function MetricCard({ label, value, icon }: { label: string; value: string; icon: string }) {
  return (
    <div className="bg-slate-800/50 rounded-lg p-3 text-center">
      <div className="text-2xl mb-1">{icon}</div>
      <div className="text-xs text-slate-400 mb-1">{label}</div>
      <div className="text-sm font-semibold text-white">{value}</div>
    </div>
  );
}
