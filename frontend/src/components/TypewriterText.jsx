import React, { useState, useEffect, useRef } from "react";

export default function TypewriterText({ text, speed = 22, delay = 0, onDone }) {
  const [displayed, setDisplayed] = useState("");
  const [done, setDone] = useState(false);
  const onDoneRef = useRef(onDone);
  useEffect(() => { onDoneRef.current = onDone; });

  useEffect(() => {
    setDisplayed("");
    setDone(false);
    let i = 0;
    let intervalId = null;
    const timeoutId = setTimeout(() => {
      if (!text) { onDoneRef.current?.(); return; }
      intervalId = setInterval(() => {
        i += 1;
        setDisplayed(text.slice(0, i));
        if (i >= text.length) {
          setDone(true);
          clearInterval(intervalId);
          onDoneRef.current?.();
        }
      }, speed);
    }, delay);
    return () => {
      clearTimeout(timeoutId);
      if (intervalId) clearInterval(intervalId);
    };
  }, [text, speed, delay]);

  return (
    <>
      {displayed}
      <span className={`narrative-cursor${done ? " done" : ""}`} aria-hidden="true" />
    </>
  );
}
