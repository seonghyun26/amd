#!/usr/bin/env bash
# prepare.sh — Set up the alanine dipeptide system for the metadynamics example.
# Run this once before run.py. Requires GROMACS installed and 'gmx' in PATH.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Alanine dipeptide — system preparation ==="
echo "Working in: $SCRIPT_DIR"
echo ""

# ── 1. Generate topology ─────────────────────────────────────────────────────
echo "[1/4] Running pdb2gmx (CHARMM36m, no water, ignoring H in PDB)..."
# Stdin "0\n0\n": select no extra N/C terminus groups (ACE and NME ARE the caps)
printf "0\n0\n" | gmx pdb2gmx \
    -f ala2.pdb \
    -o conf_raw.gro \
    -p topol.top \
    -ff charmm36m \
    -water none \
    -ignh \
    -v 2>&1 | tail -20

echo ""
echo "[2/4] Creating dodecahedron box (4 nm — large enough for 1.2 nm cutoffs)..."
gmx editconf \
    -f conf_raw.gro \
    -o ala2_box.gro \
    -bt dodecahedron \
    -d 1.5 \
    -c 2>&1 | tail -5

# ── 2. Energy minimization ───────────────────────────────────────────────────
echo ""
echo "[3/4] Energy minimization..."
gmx grompp \
    -f em.mdp \
    -c ala2_box.gro \
    -p topol.top \
    -o em.tpr \
    -maxwarn 2 2>&1 | tail -10

gmx mdrun -v -deffnm em -ntmpi 1 2>&1 | tail -5

# Use minimized structure as production starting config
cp em.gro ala2.gro

# ── 3. Verify atom indices ───────────────────────────────────────────────────
echo ""
echo "[4/4] Verifying atom indices for phi/psi..."
echo ""
echo "First 25 atoms of ala2.gro:"
head -27 ala2.gro
echo ""
echo "Expected indices for PLUMED:"
echo "  phi: atoms 5,7,9,15  →  CY(ACE) – N(ALA) – CA(ALA) – C(ALA)"
echo "  psi: atoms 7,9,15,17 →  N(ALA)  – CA(ALA) – C(ALA) – N(NME)"
echo ""

# Quick sanity check: atom 5 should be CY, atom 7 should be N
ATOM5=$(awk 'NR==7{print $2}' ala2.gro)   # GRO line 2=title, 3=natoms, 4+=atoms → atom 5 is line 7 (0-indexed: +2 header)
ATOM7=$(awk 'NR==9{print $2}' ala2.gro)

echo "Atom 5 name (expected CY):  $ATOM5"
echo "Atom 7 name (expected N):   $ATOM7"
echo ""

if [[ "$ATOM5" == "CY" ]] && [[ "$ATOM7" == "N" ]]; then
    echo "✓ Atom indices look correct."
else
    echo "⚠ Atom names don't match expectations."
    echo "  Check the first 25 atoms above and update phi/psi atom lists in run.py if needed."
fi

echo ""
echo "=== Setup complete ==="
echo "Files ready:"
echo "  ala2.gro  — minimized coordinates"
echo "  topol.top — CHARMM36m topology"
echo ""
echo "Next step: python run.py"
