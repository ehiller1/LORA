import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Lock, Unlock, AlertCircle, CheckCircle2, Info } from 'lucide-react';
import { ComparisonResult } from '../types';

interface CleanRoomCompareProps {
  comparison: ComparisonResult;
}

export default function CleanRoomCompare({ comparison }: CleanRoomCompareProps) {
  const metrics = [
    {
      label: 'iROAS',
      cleanRoom: comparison.clean_room_roas,
      fullData: comparison.full_data_roas,
      delta: comparison.roas_delta_pct,
      format: (v: number) => `${v.toFixed(2)}x`,
      icon: TrendingUp,
    },
    {
      label: 'Revenue',
      cleanRoom: comparison.clean_room_revenue,
      fullData: comparison.full_data_revenue,
      delta: comparison.revenue_delta_pct,
      format: (v: number) => `$${(v / 1000000).toFixed(2)}M`,
      icon: TrendingUp,
    },
    {
      label: 'Accuracy',
      cleanRoom: comparison.clean_room_accuracy,
      fullData: comparison.full_data_accuracy,
      delta: comparison.accuracy_delta_pct,
      format: (v: number) => `${(v * 100).toFixed(1)}%`,
      icon: CheckCircle2,
    },
    {
      label: 'SKUs Optimized',
      cleanRoom: comparison.clean_room_skus,
      fullData: comparison.full_data_skus,
      delta: comparison.sku_delta_pct,
      format: (v: number) => v.toString(),
      icon: TrendingUp,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header with Explanation */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-xl p-6">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-white rounded-lg shadow-sm">
            <Info className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              📊 Clean Room vs Federation Comparison
            </h2>
            <p className="text-gray-700 leading-relaxed">
              This comparison shows the performance difference between using <strong>clean room data only</strong> (limited fields, aggregated data)
              versus <strong>federated LoRA adapters</strong> with full data access through manufacturer adapters.
            </p>
          </div>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((metric, index) => {
          const Icon = metric.icon;
          const isPositive = metric.delta > 0;

          return (
            <motion.div
              key={metric.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden hover:shadow-xl transition-shadow"
            >
              {/* Header */}
              <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-4 py-3 border-b border-gray-200">
                <div className="flex items-center gap-2">
                  <Icon className="w-4 h-4 text-gray-600" />
                  <h3 className="font-semibold text-gray-900 text-sm">{metric.label}</h3>
                </div>
              </div>

              {/* Values */}
              <div className="p-4 space-y-3">
                {/* Clean Room */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Lock className="w-4 h-4 text-amber-500" />
                    <span className="text-xs text-gray-600">Clean Room</span>
                  </div>
                  <span className="font-mono text-sm font-semibold text-gray-700">
                    {metric.format(metric.cleanRoom)}
                  </span>
                </div>

                {/* Full Data */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Unlock className="w-4 h-4 text-green-500" />
                    <span className="text-xs text-gray-600">Federation</span>
                  </div>
                  <span className="font-mono text-sm font-bold text-gray-900">
                    {metric.format(metric.fullData)}
                  </span>
                </div>

                {/* Delta */}
                <div className={`
                  flex items-center justify-center gap-2 py-2 px-3 rounded-lg
                  ${isPositive ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}
                `}>
                  {isPositive ? (
                    <TrendingUp className="w-4 h-4 text-green-600" />
                  ) : (
                    <TrendingDown className="w-4 h-4 text-red-600" />
                  )}
                  <span className={`font-bold text-sm ${isPositive ? 'text-green-700' : 'text-red-700'}`}>
                    {isPositive ? '+' : ''}{metric.delta.toFixed(1)}%
                  </span>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Side-by-Side Comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Clean Room Only */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white rounded-xl shadow-lg border-2 border-amber-200 overflow-hidden"
        >
          <div className="bg-gradient-to-r from-amber-500 to-amber-600 px-6 py-4 text-white">
            <div className="flex items-center gap-3">
              <Lock className="w-6 h-6" />
              <div>
                <h3 className="text-lg font-bold">Clean Room Only</h3>
                <p className="text-sm text-amber-100">Limited data access</p>
              </div>
            </div>
          </div>

          <div className="p-6 space-y-4">
            <div className="space-y-2">
              <h4 className="font-semibold text-gray-900 text-sm mb-3">❌ Limitations:</h4>
              {comparison.missing_capabilities.map((cap, i) => (
                <div key={i} className="flex items-start gap-2 text-sm">
                  <AlertCircle className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">{cap}</span>
                </div>
              ))}
            </div>

            {comparison.blocked_fields.length > 0 && (
              <div className="pt-4 border-t border-gray-200">
                <h4 className="font-semibold text-gray-900 text-sm mb-2">🔒 Blocked Fields:</h4>
                <div className="flex flex-wrap gap-2">
                  {comparison.blocked_fields.slice(0, 6).map((field, i) => (
                    <span key={i} className="text-xs bg-amber-100 text-amber-800 px-2 py-1 rounded-full font-mono">
                      {field}
                    </span>
                  ))}
                  {comparison.blocked_fields.length > 6 && (
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                      +{comparison.blocked_fields.length - 6} more
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        </motion.div>

        {/* Federation */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white rounded-xl shadow-lg border-2 border-green-200 overflow-hidden"
        >
          <div className="bg-gradient-to-r from-green-500 to-green-600 px-6 py-4 text-white">
            <div className="flex items-center gap-3">
              <Unlock className="w-6 h-6" />
              <div>
                <h3 className="text-lg font-bold">Federated LoRA</h3>
                <p className="text-sm text-green-100">Full data access</p>
              </div>
            </div>
          </div>

          <div className="p-6 space-y-4">
            <div className="space-y-2">
              <h4 className="font-semibold text-gray-900 text-sm mb-3">✅ Advantages:</h4>
              {[
                'Margin-aware allocation',
                'Stock-out avoidance',
                'Promotional timing optimization',
                'Price elasticity modeling',
                '50% more SKU coverage',
                'Private manufacturer data access',
              ].map((adv, i) => (
                <div key={i} className="flex items-start gap-2 text-sm">
                  <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">{adv}</span>
                </div>
              ))}
            </div>

            <div className="pt-4 border-t border-gray-200">
              <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                <p className="text-sm text-green-800 font-semibold">
                  🎯 Result: <span className="text-green-900">{comparison.roas_delta_pct.toFixed(1)}% better performance</span>
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Key Insight */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="bg-gradient-to-r from-purple-50 to-pink-50 border-2 border-purple-200 rounded-xl p-6"
      >
        <div className="flex items-start gap-4">
          <div className="p-3 bg-white rounded-lg shadow-sm">
            <TrendingUp className="w-6 h-6 text-purple-600" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">💡 Key Insight</h3>
            <p className="text-gray-700 leading-relaxed">
              By federating <strong>Generic LLM + Industry LoRA + Manufacturer LoRA</strong>, we achieve{' '}
              <span className="font-bold text-purple-700">{comparison.roas_delta_pct.toFixed(1)}% better ROAS</span> and{' '}
              <span className="font-bold text-purple-700">{comparison.sku_delta_pct.toFixed(0)}% more SKU coverage</span>{' '}
              compared to clean room only. The manufacturer adapter provides access to private metrics (margin, stock, pricing)
              that are blocked in clean rooms, enabling superior optimization.
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
