"use client";

import React from "react";
import { motion } from "framer-motion";
import { Shield, LayoutDashboard, Info, BookOpen } from "lucide-react";

export default function Navbar() {
    return (
        <nav className="fixed top-0 left-0 right-0 z-[100] border-b border-white/10 bg-deep-black/60 backdrop-blur-md">
            <div className="container mx-auto max-w-7xl px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-3 group cursor-pointer">
                    <motion.div
                        whileHover={{ scale: 1.1, rotate: 5 }}
                        className="w-10 h-10 bg-neon-lime rounded-lg flex items-center justify-center shadow-[0_0_20px_rgba(193,255,0,0.4)]"
                    >
                        <Shield className="text-black" size={24} strokeWidth={2.5} />
                    </motion.div>
                    <div className="flex flex-col">
                        <span className="font-black text-xl tracking-tighter text-white leading-none">TRUTH<span className="text-neon-lime">_</span>ENGINE</span>
                        <span className="text-[10px] font-mono text-neon-lime leading-none tracking-[0.2em] mt-1">VERIFICATION_SYSTEM</span>
                    </div>
                </div>

                <div className="hidden md:flex items-center gap-10">
                    {[
                        { name: "Solutions", icon: Shield, active: true },
                        { name: "Documentation", icon: BookOpen },
                        { name: "Live_Monitor", icon: LayoutDashboard },
                        { name: "About", icon: Info },
                    ].map((item) => (
                        <a
                            key={item.name}
                            href="#"
                            className={`group flex items-center gap-2 text-[10px] font-black tracking-[0.15em] transition-all duration-300 uppercase ${item.active ? "text-neon-lime" : "text-slate-400 hover:text-white"}`}
                        >
                            <item.icon size={14} className={`transition-colors ${item.active ? "text-neon-lime" : "group-hover:text-neon-lime"}`} />
                            {item.name}
                        </a>
                    ))}
                </div>

                <div className="flex items-center gap-6">
                    <button className="text-[10px] font-black uppercase tracking-[0.15em] text-slate-500 hover:text-white transition-colors">
                        Login_Access
                    </button>
                    <button className="px-6 py-2.5 bg-neon-lime/10 border border-neon-lime/20 hover:border-neon-lime/50 hover:bg-neon-lime/20 text-neon-lime text-[10px] font-black uppercase tracking-[0.15em] rounded-md transition-all duration-500 shadow-[0_0_15px_rgba(193,255,0,0.1)]">
                        Request_API_Key
                    </button>
                </div>
            </div>
        </nav>
    );
}
