import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

export const formatNumber = (num: number): string => {
    return new Intl.NumberFormat("en-IN", { maximumSignificantDigits: 3 }).format(num);
};

export const formatCurrency = (num: number): string => {
    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumSignificantDigits: 3,
    }).format(num);
};
