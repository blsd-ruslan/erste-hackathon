'use client'

import React, {useEffect, useState} from 'react'
import Image from 'next/image'
import Link from 'next/link'
import {
    LayoutGrid,
    BarChart3,
    Wallet,
    Users,
    Settings,
    Shield,
    HelpCircle,
    Moon,
    ChevronDown,
    ScanQrCode
} from 'lucide-react'
import { Toggle } from "@geist-ui/react"
import {usePathname} from "next/navigation";

type NavItem = {
    icon: React.ReactElement;
    label: string;
    href: string;
};

export default function Sidebar() {
    const [isDarkMode, setIsDarkMode] = useState(true);
    const [data, setData] = useState(null);
    const pathName = usePathname();

    useEffect(() => {
        fetch('/user-example.json')
            .then((response) => response.json())
            .then((jsonData) => setData(jsonData))
            .catch((error) => console.error('Error loading JSON data:', error));
    }, []);

    const mainNavItems: NavItem[] = [
        { icon: <LayoutGrid className="w-5 h-5" />, label: 'Dashboard', href: '/' },
        { icon: <ScanQrCode className="w-5 h-5" />, label: 'Add purchase', href: '/scan' },
        { icon: <BarChart3 className="w-5 h-5" />, label: 'Analytics', href: '#' },
        { icon: <Wallet className="w-5 h-5" />, label: 'My Wallet', href: '#' },
        { icon: <Users className="w-5 h-5" />, label: 'Accounts', href: '#' },
        { icon: <Settings className="w-5 h-5" />, label: 'Settings', href: '#' },
    ];

    const secondaryNavItems: NavItem[] = [
        { icon: <Shield className="w-5 h-5" />, label: 'Security', href: '/security' },
        { icon: <HelpCircle className="w-5 h-5" />, label: 'Support', href: '/support' },
    ];

    return (
        <div style={{height: '85vh'}} className="hidden md:flex flex-col justify-between rounded-3xl w-64 bg-[#1B1932] text-white p-4 ml-6 mt-6">
            <div>
                <div className="flex items-center gap-2 mb-8">
                    <Image src="/erste-logo.jpg" className="rounded-full mr-2" width="32" height="32" alt="erste logo" priority />
                    <span className="text-xl font-semibold">ERSTE +</span>
                </div>

                {/* Main Navigation */}
                <nav className="space-y-2">
                    {mainNavItems.map((item) => (
                        <Link key={item.label} href={item.href} className={`flex items-center gap-3 px-4 py-2.5 rounded-lg transition-colors ${
                                    pathName === item.href
                                        ? 'bg-indigo-600 text-white'
                                        : 'text-gray-400 hover:text-white hover:bg-white/10'
                                }`}
                            >
                                {item.icon}
                                <span>{item.label}</span>
                        </Link>
                    ))}
                </nav>

                {/* Divider */}
                <div className="h-px bg-white/10 my-4" />

                {/* Secondary Navigation */}
                <nav className="space-y-2">
                    {secondaryNavItems.map((item) => (
                        <Link key={item.label} href={item.href} className={`flex items-center gap-3 px-4 py-2.5 rounded-lg transition-colors ${
                                pathName === item.href
                                    ? 'bg-[#276FF2] text-white'
                                    : 'text-gray-400 hover:text-white hover:bg-white/10'
                            }`}>
                                {item.icon}
                                <span>{item.label}</span>
                        </Link>
                    ))}
                </nav>

                {/* Dark Mode Toggle */}
                <div className="flex items-center gap-3 px-4 py-2.5 text-gray-400">
                    <Moon className="w-5 h-5" />
                    <span>Dark Mode</span>
                    <Toggle
                        checked={isDarkMode}
                        onChange={() => setIsDarkMode(!isDarkMode)}
                        className="ml-auto data-[state=checked]:bg-indigo-600"
                    />
                </div>
            </div>

            {/* User Profile */}
            <div className="flex max-h-fit items-center gap-3 px-4 mt-2">
                <Image src="/meMac.png" width={40} height={40} alt="User avatar" className="rounded-full" />
                <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-medium truncate">{data?.username || "John Doe"}</h3>
                    <p className="text-xs text-gray-400 truncate">Web Developer</p>
                </div>
                <button className="text-gray-400 hover:text-white">
                    <ChevronDown className="w-4 h-4" />
                </button>
            </div>
        </div>
    );
}