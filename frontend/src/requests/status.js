// Status shown in lists and forms. Tone follows the colour rule: yellow (accent) for pending, green for approved or
// completed, red for rejected, grey (muted) for cancelled. `group` feeds the list tabs.
import { __ } from "@/api/i18n";

const BY_STATUS = {
	Open: ["Pending", "accent", "pending"],
	Draft: ["Pending", "accent", "pending"],
	Unpaid: ["Pending", "accent", "pending"],
	Submitted: ["Pending", "accent", "pending"],
	"Partially Paid": ["Partially paid", "accent", "pending"],
	Approved: ["Approved", "success", "approved"],
	Paid: ["Paid", "success", "approved"],
	Claimed: ["Claimed", "success", "approved"],
	Returned: ["Returned", "success", "approved"],
	"Partly Claimed and Returned": ["Partly claimed and returned", "success", "approved"],
	Rejected: ["Rejected", "danger", "closed"],
	Cancelled: ["Cancelled", "muted", "closed"],
};

/** { label, tone, group } for a document. `field` is the status field of the doctype, or null if it has none. */
export function statusOf(doc, field) {
	if (doc.docstatus === 2) return { label: __("Cancelled"), tone: "muted", group: "closed" };
	const known = field && BY_STATUS[doc[field]];
	if (known) return { label: __(known[0]), tone: known[1], group: known[2] };
	if (field && doc[field]) return { label: doc[field], tone: "accent", group: "pending" };
	// No status field: a submitted document is the approved one
	return doc.docstatus === 1
		? { label: __("Approved"), tone: "success", group: "approved" }
		: { label: __("Pending"), tone: "accent", group: "pending" };
}
