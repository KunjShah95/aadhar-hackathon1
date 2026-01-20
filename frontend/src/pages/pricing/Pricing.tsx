import { motion } from 'framer-motion';
import { Check, Shield, Zap, ArrowRight } from 'lucide-react';

const plans = [
    {
        name: 'Researcher',
        price: '0',
        description: 'For students and academic research.',
        features: [
            'Access to aggregated demographics',
            'Weekly data snapshots',
            'Community support',
            'API Rate limit: 100/day'
        ],
        cta: 'Start Free',
        popular: false
    },
    {
        name: 'Enterprise',
        price: '499',
        description: 'For banks, fintechs, and government agencies.',
        features: [
            'Real-time biometric telemetry',
            'Fraud prediction engine (LightGBM)',
            'Dedicated secure endpoints',
            '24/7 SLA Support',
            'Unlimited API Access'
        ],
        cta: 'Contact Sales',
        popular: true
    },
    {
        name: 'Developer API',
        price: '0.01',
        unit: ' / call',
        description: 'Pay-as-you-go for startups.',
        features: [
            'e-KYC Verification API',
            'Anomaly Detection Webhooks',
            'Usage dashboard',
            'Sandbox environment'
        ],
        cta: 'Get API Key',
        popular: false
    }
];

export default function Pricing() {
    return (
        <div className="space-y-12 pb-20">
            <div className="text-center space-y-4 max-w-2xl mx-auto">
                <h1 className="text-4xl font-bold font-display text-white">Commercial Access</h1>
                <p className="text-muted-foreground text-lg">
                    Scale your secure identity infrastructure with our production-ready tiers.
                    <br />
                    <span className="text-primary text-sm font-mono mt-2 inline-block">SECURE // COMPLIANT // SCALABLE</span>
                </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
                {plans.map((plan, i) => (
                    <motion.div
                        key={plan.name}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.1 }}
                        className={`relative rounded-2xl border p-8 backdrop-blur-sm transition-all hover:-translate-y-2 hover:shadow-2xl ${plan.popular
                            ? 'border-primary/50 bg-primary/5 shadow-primary/10'
                            : 'border-white/10 bg-white/5 hover:border-white/20'
                            }`}
                    >
                        {plan.popular && (
                            <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-primary text-black text-xs font-bold uppercase tracking-wider shadow-lg shadow-primary/20">
                                Most Popular
                            </div>
                        )}

                        <div className="mb-8">
                            <h3 className="text-xl font-bold text-white mb-2">{plan.name}</h3>
                            <p className="text-sm text-muted-foreground min-h-[40px]">{plan.description}</p>
                        </div>

                        <div className="mb-8 flex items-baseline">
                            <span className="text-4xl font-bold text-white">${plan.price}</span>
                            {plan.unit && <span className="text-muted-foreground ml-2">{plan.unit}</span>}
                            {!plan.unit && <span className="text-muted-foreground ml-2">/ month</span>}
                        </div>

                        <ul className="space-y-4 mb-8">
                            {plan.features.map((feature) => (
                                <li key={feature} className="flex items-start gap-3 text-sm text-gray-300">
                                    <Check className="h-5 w-5 text-primary shrink-0" />
                                    {feature}
                                </li>
                            ))}
                        </ul>

                        <button className={`w-full py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all ${plan.popular
                            ? 'bg-primary text-black hover:bg-primary/90 shadow-lg'
                            : 'bg-white/10 text-white hover:bg-white/20'
                            }`}>
                            {plan.cta}
                            <ArrowRight className="h-4 w-4" />
                        </button>
                    </motion.div>
                ))}
            </div>

            {/* Enterprise Trust Section */}
            <div className="border border-white/5 rounded-2xl bg-white/5 p-8 mt-12 flex flex-col md:flex-row items-center justify-between gap-8">
                <div className="flex items-center gap-4">
                    <div className="p-3 rounded-full bg-emerald-500/10 text-emerald-500">
                        <Shield className="h-8 w-8" />
                    </div>
                    <div>
                        <h3 className="text-lg font-bold text-white">Bank-Grade Security</h3>
                        <p className="text-sm text-muted-foreground">ISO 27001 Certified • End-to-End Encryption • SOC 2 Type II</p>
                    </div>
                </div>
                <div className="h-12 w-px bg-white/10 hidden md:block" />
                <div className="flex items-center gap-4">
                    <div className="p-3 rounded-full bg-blue-500/10 text-blue-500">
                        <Zap className="h-8 w-8" />
                    </div>
                    <div>
                        <h3 className="text-lg font-bold text-white">99.99% Uptime SLA</h3>
                        <p className="text-sm text-muted-foreground">Redundant infrastructure across 3 availability zones.</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
