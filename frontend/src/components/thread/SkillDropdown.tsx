"use client";

import { useEffect, useRef } from "react";

export interface Skill {
  name: string;
  description: string;
  triggers: string[];
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

  // Filter skills based on filter text
  const filteredSkills = skills.filter(
    (skill) =>
      skill.name.toLowerCase().includes(filter.toLowerCase()) ||
      skill.description.toLowerCase().includes(filter.toLowerCase())
  );

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

  if (filteredSkills.length === 0) {
    return null;
  }

  return (
    <div
      ref={ref}
      className="absolute z-50 w-72 rounded-lg border bg-white shadow-lg"
      style={{ top: position.top + 36, left: position.left }}
    >
      <div className="max-h-64 overflow-y-auto p-1">
        {filteredSkills.map((skill) => (
          <button
            key={skill.name}
            className="flex w-full cursor-pointer items-start gap-2 rounded-md p-2 text-left hover:bg-gray-100"
            onClick={() => onSelect(skill)}
          >
            <span className="flex h-6 min-w-6 items-center justify-center rounded bg-primary/10 px-1 text-xs font-medium text-primary">
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
