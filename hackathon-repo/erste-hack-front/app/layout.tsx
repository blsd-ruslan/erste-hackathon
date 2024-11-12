'use client'

import localFont from "next/font/local";
import "./globals.css";
import { GeistProvider, CssBaseline } from '@geist-ui/react';
import {Themes} from "@geist-ui/core";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

const myDarkTheme = Themes.createFromDark({
  type: 'myTheme',
  palette: {
    background: '#1B1932',
  },
})

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className='h-full'>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased h-full`}
      >
        <GeistProvider themes={[myDarkTheme]} themeType="myTheme">
          <CssBaseline/>
          {children}
        </GeistProvider>
      </body>
    </html>
  );
}
