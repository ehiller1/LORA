import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Play,
  CheckCircle2,
  Loader2,
  AlertCircle,
  ChevronRight,
  Settings,
  HelpCircle,
} from 'lucide-react';
import FederationGraph from '../components/FederationGraph';
import CleanRoomCompare from '../components/CleanRoomCompare';
import { endpoints } from '../api/apiClient';
import { DemoResults, WorkflowStep } from '../types';

export default function Dashboard() {
  const [demoResults, setDemoResults] = useState<DemoResults | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  
  // Configuration
  const [budget, setBudget] = useState(2500000);
  const [roasFloor, setRoasFloor] = useState(3.0);
  const [expShare, setExpShare] = useState(0.1);
  const [showConfig, setShowConfig] = useState(false);

  const workflowSteps: WorkflowStep[] = [
    {
      id: 'harmonization',
      title: 'Data Harmonization',
      description: 'Transform retailer data to RMIS schema',
      status: 'pending',
      icon: '🔄',
    },
    {
      id: 'planning',
      title: 'Plan Generation',
      description: 'Generate optimized campaign plans',
      status: 'pending',
      icon: '📊',
    },
    {
      id: 'comparison',
      title: 'Clean Room Comparison',
      description: 'Compare federation vs clean room',
      status: 'pending',
      icon: '⚖️',
    },
    {
      id: 'creatives',
      title: 'Creative Generation',
      description: 'Generate compliant ad copy',
      status: 'pending',
      icon: '✨',
    },
  ];

  const runDemo = async () => {
    setIsRunning(true);
    setError(null);
    setCurrentStep(0);

    try {
      // Simulate step-by-step execution
      for (let i = 0; i < workflowSteps.length; i++) {
        setCurrentStep(i);
        await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate processing
      }

      const response = await endpoints.runDemo({
        budget,
        roas_floor: roasFloor,
        exp_share: expShare,
      });

      setDemoResults(response.data);
      setCurrentStep(workflowSteps.length);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to run demo');
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                🎯 RMN LoRA Federation Demo
              </h1>
              <p className="text-gray-600 text-sm mt-1">
                Demonstrating superior retail media optimization through federated LoRA adapters
              </p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setShowConfig(!showConfig)}
                className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                <Settings className="w-4 h-4" />
                <span className="text-sm font-medium">Configure</span>
              </button>
              <a
                href="/docs"
                className="flex items-center gap-2 px-4 py-2 bg-blue-50 hover:bg-blue-100 text-blue-600 rounded-lg transition-colors"
              >
                <HelpCircle className="w-4 h-4" />
                <span className="text-sm font-medium">Help</span>
              </a>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Configuration Panel */}
        <AnimatePresence>
          {showConfig && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-6 bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden"
            >
              <div className="p-6 space-y-4">
                <h3 className="font-bold text-lg text-gray-900">⚙️ Demo Configuration</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Total Budget
                    </label>
                    <input
                      type="number"
                      value={budget}
                      onChange={(e) => setBudget(Number(e.target.value))}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      step={100000}
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      ${(budget / 1000000).toFixed(2)}M
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Minimum ROAS
                    </label>
                    <input
                      type="number"
                      value={roasFloor}
                      onChange={(e) => setRoasFloor(Number(e.target.value))}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      step={0.1}
                      min={1}
                      max={10}
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      {roasFloor.toFixed(1)}x minimum return
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Experiment Budget %
                    </label>
                    <input
                      type="number"
                      value={expShare * 100}
                      onChange={(e) => setExpShare(Number(e.target.value) / 100)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      step={5}
                      min={0}
                      max={30}
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      {(expShare * 100).toFixed(0)}% for experiments
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Main Content */}
        {!demoResults && !isRunning ? (
          /* Welcome Screen */
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-16"
          >
            <div className="max-w-3xl mx-auto">
              <div className="mb-8">
                <div className="inline-block p-4 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl shadow-xl mb-6">
                  <Play className="w-16 h-16 text-white" />
                </div>
                <h2 className="text-4xl font-bold text-gray-900 mb-4">
                  Ready to See the Power of Federation?
                </h2>
                <p className="text-xl text-gray-600 leading-relaxed">
                  This demo will show you how combining <strong>Generic LLM + Industry LoRA + Manufacturer LoRA</strong>{' '}
                  delivers <strong className="text-green-600">25%+ better ROAS</strong> compared to clean-room-only analytics.
                </p>
              </div>

              {/* What You'll See */}
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8 mb-8 text-left">
                <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">
                  📋 What You'll See
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {workflowSteps.map((step, index) => (
                    <div key={step.id} className="flex items-start gap-4">
                      <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold shadow-lg">
                        {index + 1}
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-1">
                          {step.icon} {step.title}
                        </h4>
                        <p className="text-sm text-gray-600">{step.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Run Button */}
              <button
                onClick={runDemo}
                className="inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold rounded-xl shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-200"
              >
                <Play className="w-6 h-6" />
                <span className="text-lg">Run Federation Demo</span>
                <ChevronRight className="w-5 h-5" />
              </button>

              <p className="text-sm text-gray-500 mt-4">
                Demo takes approximately 10 seconds to complete
              </p>
            </div>
          </motion.div>
        ) : isRunning ? (
          /* Loading State with Progress */
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="py-16"
          >
            <div className="max-w-2xl mx-auto">
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
                <div className="text-center mb-8">
                  <Loader2 className="w-16 h-16 text-blue-600 animate-spin mx-auto mb-4" />
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">
                    Running Federation Demo...
                  </h3>
                  <p className="text-gray-600">
                    Composing adapters and generating results
                  </p>
                </div>

                {/* Progress Steps */}
                <div className="space-y-4">
                  {workflowSteps.map((step, index) => {
                    const isActive = index === currentStep;
                    const isCompleted = index < currentStep;

                    return (
                      <motion.div
                        key={step.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className={`
                          flex items-center gap-4 p-4 rounded-lg border-2 transition-all
                          ${isActive ? 'border-blue-500 bg-blue-50' : ''}
                          ${isCompleted ? 'border-green-500 bg-green-50' : ''}
                          ${!isActive && !isCompleted ? 'border-gray-200 bg-gray-50' : ''}
                        `}
                      >
                        <div className={`
                          flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center font-bold
                          ${isActive ? 'bg-blue-600 text-white' : ''}
                          ${isCompleted ? 'bg-green-600 text-white' : ''}
                          ${!isActive && !isCompleted ? 'bg-gray-300 text-gray-600' : ''}
                        `}>
                          {isCompleted ? (
                            <CheckCircle2 className="w-6 h-6" />
                          ) : isActive ? (
                            <Loader2 className="w-6 h-6 animate-spin" />
                          ) : (
                            index + 1
                          )}
                        </div>
                        <div className="flex-1">
                          <h4 className="font-semibold text-gray-900">
                            {step.icon} {step.title}
                          </h4>
                          <p className="text-sm text-gray-600">{step.description}</p>
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              </div>
            </div>
          </motion.div>
        ) : demoResults ? (
          /* Results View */
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-8"
          >
            {/* Success Banner */}
            <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-xl p-6">
              <div className="flex items-center gap-4">
                <CheckCircle2 className="w-12 h-12 text-green-600" />
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-1">
                    ✅ Demo Complete!
                  </h2>
                  <p className="text-gray-700">
                    Federation achieved <strong className="text-green-700">
                      {demoResults.steps.comparison.roas_delta_pct.toFixed(1)}% better ROAS
                    </strong> compared to clean room only
                  </p>
                </div>
              </div>
            </div>

            {/* Results Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Main Content - 2 columns */}
              <div className="lg:col-span-2 space-y-6">
                <CleanRoomCompare comparison={demoResults.steps.comparison} />
              </div>

              {/* Sidebar - 1 column */}
              <div className="space-y-6">
                <FederationGraph
                  activeAdapters={demoResults.steps.full_plan.adapters_used}
                  compositionData={demoResults.steps.visualization}
                />

                {/* Quick Actions */}
                <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
                  <h3 className="font-bold text-gray-900 mb-4">🚀 Next Steps</h3>
                  <div className="space-y-3">
                    <button className="w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors">
                      Export Results
                    </button>
                    <button
                      onClick={runDemo}
                      className="w-full px-4 py-3 bg-gray-100 hover:bg-gray-200 text-gray-900 rounded-lg font-medium transition-colors"
                    >
                      Run Again
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        ) : null}

        {/* Error State */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-2xl mx-auto"
          >
            <div className="bg-red-50 border-2 border-red-200 rounded-xl p-6">
              <div className="flex items-start gap-4">
                <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0" />
                <div>
                  <h3 className="font-bold text-red-900 mb-2">Error Running Demo</h3>
                  <p className="text-red-700 text-sm">{error}</p>
                  <button
                    onClick={runDemo}
                    className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors"
                  >
                    Try Again
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
