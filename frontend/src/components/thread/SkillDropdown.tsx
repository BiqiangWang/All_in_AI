"use client";

import { useEffect, useRef, useState } from "react";

export interface Skill {
  name: string;
  description: string;
  triggers: string[];
  path?: string;
}

interface SkillDropdownProps {
  skills: Skill[];
  filter: string;  // e.g., "nuwa" from "/nuwa"
  position: { top: number; left: number };
  onSelect: (skill: Skill) => void;
  onClose: () => void;
}

export function SkillDropdown({
  skills,
  filter,
  position,
  onSelect,
  onClose,
}: SkillDropdownProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [selectedIndex, setSelectedIndex] = useState(0);

  // Filter skills based on filter text
  const filteredSkills = skills.filter(
    (skill) =>
      skill.name.toLowerCase().includes(filter.toLowerCase()) ||
      skill.description.toLowerCase().includes(filter.toLowerCase())
  );

  // Reset selected index when filter changes
  useEffect(() => {
    setSelectedIndex(0);
  }, [filter]);

  // Handle click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        onClose();
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [onClose]);

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev < filteredSkills.length - 1 ? prev + 1 : 0
        );
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev > 0 ? prev - 1 : filteredSkills.length - 1
        );
      } else if (e.key === "Tab") {
        e.preventDefault();
        if (filteredSkills[selectedIndex]) {
          onSelect(filteredSkills[selectedIndex]);
        }
      } else if (e.key === "Escape") {
        e.preventDefault();
        onClose();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [filteredSkills, selectedIndex, onSelect, onClose]);

  if (filteredSkills.length === 0) {
    return null;
  }

  return (
    <div
      ref={ref}
      className="fixed z-50 w-72 rounded-lg border bg-white shadow-lg"
      style={{ top: position.top + 36, left: position.left }}
    >
      <div className="max-h-64 overflow-y-auto p-1">
        {filteredSkills.map((skill, index) => (
          <button
            key={skill.name}
            className={`flex w-full cursor-pointer items-start gap-2 rounded-md p-2 text-left transition-colors ${
              index === selectedIndex
                ? "bg-blue-50 text-blue-900"
                : "hover:bg-gray-100"
            }`}
            onClick={() => onSelect(skill)}
            onMouseEnter={() => setSelectedIndex(index)}
          >
            <span className={`flex h-6 min-w-6 items-center justify-center rounded px-1 text-xs font-medium ${
                index === selectedIndex ? "bg-blue-200 text-blue-700" : "bg-primary/10 text-primary"
              }`}>
              /
            </span>
            <div className="flex-1 overflow-hidden">
              <div className="font-medium text-gray-900">{skill.name}</div>
              <div className="truncate text-sm text-gray-500">
                {skill.description}
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
