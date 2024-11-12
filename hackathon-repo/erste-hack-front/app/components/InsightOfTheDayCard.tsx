'use client'

import {TrendingUp, Info, RefreshCw} from 'lucide-react'
import {Button, Card} from "@geist-ui/react"
import {Progress} from "@geist-ui/react"
import {useState} from "react";

interface InsightOfTheDayProps {
    product: string
    category: string
    amount: number
    percentage: number
    averageAmount: number
    onRegenerate: () => void
}

const styles = {
    card: {
        backgroundColor: '#1B1932',
        border: 'none',
        borderRadius: '1.5rem',
        display: 'flex',
        flexDirection: 'column',
        width: '100%',
        height: '100%',
        flex: 1
    },
}

export default function InsightOfTheDayCard({
                                                product = "Cappuccino",
                                                category = "Dining Out",
                                                amount = 150,
                                                percentage = 75,
                                                averageAmount = 85,
                                                onRegenerate
                                            }: InsightOfTheDayProps) {
    const [attempts, setAttempts] = useState(5)
    const handleRegenerate = () => {
        if (attempts > 0) {
            setAttempts(attempts - 1)
            onRegenerate()
        }
    }

    return (
        <Card style={styles.card} className='w-full'>
            <div className='px-4 h-80'>
                <Card.Content style={{padding: 0, height: '100%'}} className="space-y-4 pb-2">
                    <div className="flex flex-col justify-between h-full">
                        <div>
                            <div className="flex flex-row items-center justify-between">
                                <h4 className="font-semibold text-[#296FEE]">Insight of the Day</h4>
                                <Info className="h-8 w-8 pb-2 text-[#296FEE]"/>
                            </div>
                            <div className="flex items-center space-x-2 text-[#296FEE]">
                                <TrendingUp className="h-5 w-5"/>
                                <span className="text-sm font-medium">Unusual spending detected</span>
                            </div>

                            <p className="text-base text-white">
                                You spent <span className="font-bold text-[#296FEE]">€ {amount}</span> on {product} ({category}) in October.
                            </p>

                            <div className="space-y-2">
                                <div className="flex justify-between text-sm">
                                    <span className="text-gray-400">Average spending</span>
                                    <span className="text-white font-medium">€ {averageAmount}</span>
                                </div>
                                <Progress value={percentage} className="h-2 bg-gray-700">
                                    <div
                                        className="h-full bg-gradient-to-r from-amber-500 to-red-500 rounded-full transition-all"
                                        style={{width: `${percentage}%`}}
                                    />
                                </Progress>
                                <div className="flex justify-between text-sm">
                                    <span className="text-gray-400">This month&#39;s spending</span>
                                    <span className="text-white font-medium">€ {amount}</span>
                                </div>
                            </div>
                        </div>
                        <div className="bg-white/5 rounded-lg p-4 text-lg flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                            <span className="font-medium text-white">
                                {percentage}% more than usual
                            </span>
                            </div>
                            <span className="text-2xl font-bold text-[#296FEE]">+€ {amount - averageAmount}</span>
                        </div>
                    </div>
                    <div className="flex justify-center items-center px-4 pb-4">
                        <Button
                            type="success"
                            ghost
                            auto
                            onClick={handleRegenerate}
                            disabled={attempts === 0}
                            className="w-full text-white"
                        >
                            <RefreshCw className="mr-2 h-4 w-4" />
                            Regenerate ({attempts} left)
                        </Button>
                    </div>
                </Card.Content>
            </div>
        </Card>
    )
}