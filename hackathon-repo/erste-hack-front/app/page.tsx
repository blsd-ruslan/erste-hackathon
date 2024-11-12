'use client'

import Sidebar from "@/app/components/Sidebar";
import DashboardLayout from "@/app/components/DashboardLayout";

export default function Home() {
    return (
        <div className="flex min-h-screen flex-col bg-[#0D0B21]">
            <div className="flex flex-1 flex-col md:flex-row">
                <Sidebar/>

                <main className="flex-1 p-4">
                    <DashboardLayout/>
                </main>
            </div>
        </div>
    );
}
