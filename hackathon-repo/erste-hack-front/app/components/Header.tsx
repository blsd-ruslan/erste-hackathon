'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Menu, X, Sun, Moon } from '@geist-ui/icons'
import { Button } from '@geist-ui/react'

export default function Header() {
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
    const [isDarkMode, setIsDarkMode] = useState(false)

    const toggleMobileMenu = () => {
        setIsMobileMenuOpen(!isMobileMenuOpen)
    }

    const toggleDarkMode = () => {
        setIsDarkMode(!isDarkMode)
        // In a real application, you would implement the actual dark mode toggle here
        document.documentElement.classList.toggle('dark')
    }

    return (
        <header className="bg-white dark:bg-gray-800 shadow-md">
            <div className="container mx-auto px-4 py-4">
                <div className="flex items-center justify-between">
                    <Link href="/" className="text-2xl font-bold text-gray-800 dark:text-white">
                        My App
                    </Link>

                    <nav className="hidden md:flex space-x-4">
                        <Link href="/" className="text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-white">
                            Home
                        </Link>
                        <Link href="/about" className="text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-white">
                            About
                        </Link>
                        <Link href="/services" className="text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-white">
                            Services
                        </Link>
                        <Link href="/contact" className="text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-white">
                            Contact
                        </Link>
                    </nav>

                    <div className="flex items-center">
                        {/* eslint-disable-next-line @typescript-eslint/ban-ts-comment */}
                        {/*@ts-expect-error*/}
                        <Button
                            ghost
                            onClick={toggleDarkMode}
                            className="mr-2"
                            aria-label={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
                        >
                            {isDarkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
                        </Button>

                        {/* eslint-disable-next-line @typescript-eslint/ban-ts-comment */}
                        {/*@ts-expect-error*/}
                        <Button
                            ghost
                            className="md:hidden"
                            onClick={toggleMobileMenu}
                            aria-label="Toggle mobile menu"
                        >
                            {isMobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
                        </Button>
                    </div>
                </div>

                {isMobileMenuOpen && (
                    <nav className="mt-4 md:hidden">
                        <div className="flex flex-col space-y-2">
                            <Link href="/" className="text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-white">
                                Home
                            </Link>
                            <Link href="/about" className="text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-white">
                                About
                            </Link>
                            <Link href="/services" className="text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-white">
                                Services
                            </Link>
                            <Link href="/contact" className="text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-white">
                                Contact
                            </Link>
                        </div>
                    </nav>
                )}
            </div>
        </header>
    )
}