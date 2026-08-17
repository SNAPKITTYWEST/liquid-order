import Mathlib.Data.List.Basic
import Mathlib.Data.Finset.Basic

namespace Hieroglyphs

/-- A deliberately bounded alphabet for the signs in the supplied stream. -/
inductive Glyph
  | eye      -- 𓂀
  | bread    -- 𓏏
  | mouth    -- 𓂋
  | flax     -- 𓎛
  | stroke   -- 𓏤
  | god      -- 𓊹
  | ankh     -- 𓋹
  | cobra    -- 𓆣
  | sun      -- 𓇳
  | unknownA -- 𓂻
  | water    -- 𓈖
  | stool    -- 𓊪
  | owl      -- 𓅓
  | basket   -- 𓎼
deriving DecidableEq, Repr

def transliterate : Glyph → String
  | .eye      => "ir"
  | .bread    => "t"
  | .mouth    => "r"
  | .flax     => "h"
  | .stroke   => "·"
  | .god      => "nṯr"
  | .ankh     => "ꜥnḫ"
  | .cobra    => "?"
  | .sun      => "rꜥ"
  | .unknownA => "?"
  | .water    => "n"
  | .stool    => "p"
  | .owl      => "m"
  | .basket   => "g"

/-- A decoding is only certified relative to an explicit grammar and lexicon. -/
structure DecodeSpec where
  lexical     : List Glyph → Option String
  grammatical : List Glyph → Prop
  sound       : ∀ xs meaning,
                  lexical xs = some meaning → grammatical xs

/-- Concrete recognition is distinct from semantic translation. -/
def Recognized (xs : List Glyph) : Prop :=
  ∀ g, g ∈ xs →
    g = .eye      ∨ g = .bread ∨ g = .mouth  ∨ g = .flax  ∨
    g = .stroke   ∨ g = .god   ∨ g = .ankh   ∨ g = .cobra ∨
    g = .sun      ∨ g = .unknownA ∨ g = .water ∨ g = .stool ∨
    g = .owl      ∨ g = .basket

/-- A formal definition of periodicity for a list. -/
def Periodic (period xs : List Glyph) : Prop :=
  period ≠ [] ∧ ∃ k, xs = List.join (List.replicate k period)

/-- Example recurring motif — not asserted to be Egyptian grammar. -/
def Motif : List Glyph :=
  [.eye, .ankh, .god, .sun, .cobra, .unknownA,
   .water, .bread, .flax, .mouth, .stool, .owl]

example : Periodic Motif (Motif ++ Motif) := by
  refine ⟨by decide, 2, ?_⟩
  simp [Motif]

/-- A truthful result type: never manufacture a semantic translation. -/
inductive DecodeResult
  | transliteration    : List String → DecodeResult
  | grammatical        : String → DecodeResult
  | insufficientEvidence : String → DecodeResult
deriving Repr

def decode (spec : DecodeSpec) (xs : List Glyph) : DecodeResult :=
  match spec.lexical xs with
  | some meaning =>
      if spec.grammatical xs then .grammatical meaning
      else .insufficientEvidence "Lexicon returned a reading rejected by grammar."
  | none =>
      .insufficientEvidence
        "No certified lexical-and-grammatical interpretation for this glyph sequence."

theorem no_semantic_claim_without_lexicon
    (spec : DecodeSpec) (xs : List Glyph)
    (h : spec.lexical xs = none) :
    decode spec xs =
      .insufficientEvidence
        "No certified lexical-and-grammatical interpretation for this glyph sequence." := by
  simp [decode, h]

end Hieroglyphs
