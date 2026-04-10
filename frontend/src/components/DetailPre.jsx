import React from "react";
import { isEmpty } from "../utils/format";

export default function DetailPre({ text }) {
  if (isEmpty(text))
    return <p className="empty-copy">No data captured for this section.</p>;
  return <pre className="detail-pre">{text}</pre>;
}
