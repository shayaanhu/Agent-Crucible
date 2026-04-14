import React, { useState, useMemo } from "react";
import { Plus } from "../../icons";
import LabCard from "./LabCard";
import LabCreateModal from "./LabCreateModal";

const DIFFICULTY_ORDER = { beginner: 0, intermediate: 1, advanced: 2 };

export default function LabsView({ labs, onSave, onDelete, onLaunch }) {
  const [modalOpen, setModalOpen] = useState(false);
  const [editingLab, setEditingLab] = useState(null);

  const sortedLabs = useMemo(
    () => [...labs].sort((a, b) => (DIFFICULTY_ORDER[a.difficulty] ?? 99) - (DIFFICULTY_ORDER[b.difficulty] ?? 99)),
    [labs]
  );

  function handleOpenCreate() {
    setEditingLab(null);
    setModalOpen(true);
  }

  function handleOpenEdit(lab) {
    setEditingLab(lab);
    setModalOpen(true);
  }

  function handleSave(draft) {
    onSave(draft);
    setModalOpen(false);
    setEditingLab(null);
  }

  function handleClose() {
    setModalOpen(false);
    setEditingLab(null);
  }

  return (
    <div>
      <div className="section-header">
        <div className="section-title">Lab exercises</div>
        <button type="button" className="btn btn-primary" onClick={handleOpenCreate}>
          <Plus size={13} strokeWidth={1.5} /> New lab exercise
        </button>
      </div>

      {labs.length === 0 ? (
        <div className="empty-card">
          <div className="empty-card-heading">No lab exercises yet</div>
          <div className="empty-card-body">Create a lab exercise to pre-configure an attack scenario with learning objectives for students to run and reflect on.</div>
          <button type="button" className="btn btn-primary" style={{ marginTop: 12 }} onClick={handleOpenCreate}>
            <Plus size={13} strokeWidth={1.5} /> New lab exercise
          </button>
        </div>
      ) : (
        <div className="timeline-list">
          {sortedLabs.map((lab, index) => (
            <LabCard
              key={lab.id}
              lab={lab}
              index={index}
              onLaunch={onLaunch}
              onEdit={handleOpenEdit}
              onDelete={onDelete}
            />
          ))}
        </div>
      )}

      {modalOpen && (
        <LabCreateModal
          initialLab={editingLab}
          onSave={handleSave}
          onClose={handleClose}
        />
      )}
    </div>
  );
}
