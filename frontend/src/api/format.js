import dayjs from "dayjs";

export const fmtDate = (date) => (date ? dayjs(date).format("DD MMM YYYY") : "");

/** 1234.5, "EUR" -> "€1,234.50" in the user's locale; falls back to a plain number if the currency code is unknown. */
export function money(value, currency) {
	const amount = Number(value || 0);
	try {
		return new Intl.NumberFormat(undefined, { style: "currency", currency }).format(amount);
	} catch {
		return `${amount.toLocaleString(undefined, { minimumFractionDigits: 2 })} ${
			currency || ""
		}`.trim();
	}
}
