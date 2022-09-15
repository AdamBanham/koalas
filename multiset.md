# Process Mining Handbook (P14)

The standard set operators can be extended to multisets, e.g., x ∈ b2, 
b2 union b3 = b4, b5 \ b2 = b3, |b5| = 6, etc. {a ∈ b} denotes the set with all 
elements a for which b(a) ≥ 1. b(X) = largesum_{a∈X}{b(x)} is the number of 
elements in b belonging to set X, e.g., b5({x, y}) = 3+2 = 5. b ≤ b' if b(a) ≤ 
b'(a) for all a ∈ A. Hence, b3 ≤ b4 and b2 not≤ b3 (because b2 has two x’s). 
b < b' if b ≤ b'and b not= b'. Hence, b3 < b4 and b4 not< b5 (because b4 = b5).

## Membership test 

for a multiset b ∈ B(A), to test if a_1 ∈ b, b(a_1) >= 0.

## Subset test
<, <=
for a multiset b ∈ B(A), and c ∈ B(A), to test if c < b, c(a) < b(a) for every 
a ∈ A
for a multiset b ∈ B(A), and c ∈ B(A), to test if c <= b, c(a) <= b(a) for every 
a ∈ A

## Superset test
>,>=
for a multiset b ∈ B(A), and c ∈ B(A), to test if c > b, c(a) > b(a) for every 
a ∈ A
for a multiset b ∈ B(A), and c ∈ B(A), to test if c >= b, c(a) >= b(a) for every 
a ∈ A

## Intersection 
-

## Union
+

## Set Difference
/

## Fancy Membership test

is some partial trace in the language? 
i.e. < *, a, b, *> is a partial trace, where we are looking for any trace where
a followed b.


