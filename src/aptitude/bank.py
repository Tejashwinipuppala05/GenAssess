from __future__ import annotations

from typing import TypedDict


class QuestionDefinition(TypedDict):
    id: str
    question: str
    options: list[str]
    correct_answer: int
    explanation: str
    topic: str
    subtopic: str
    category: str
    difficulty: str
    estimated_time_seconds: int
    source_type: str
    tags: list[str]
    target_roles: list[str]


def _question(
    question_id: str,
    question: str,
    options: tuple[str, str, str, str],
    correct_answer: int,
    explanation: str,
    topic: str,
    difficulty: str,
    *,
    category: str = "Quantitative Aptitude",
    seconds: int = 60,
    tags: tuple[str, ...] = (),
    roles: tuple[str, ...] = (),
) -> QuestionDefinition:
    return {
        "id": question_id,
        "question": question,
        "options": list(options),
        "correct_answer": correct_answer,
        "explanation": explanation,
        "topic": topic,
        "subtopic": topic,
        "category": category,
        "difficulty": difficulty,
        "estimated_time_seconds": seconds,
        "source_type": "Original GenAssess question",
        "tags": list(tags),
        "target_roles": list(roles),
    }


QUESTION_BANK: list[QuestionDefinition] = [
    _question("qa-pct-01", "A salary of Rs. 24,000 is increased by 15%. What is the new salary?", ("Rs. 26,400", "Rs. 27,600", "Rs. 28,000", "Rs. 29,400"), 1, "15% of 24,000 is 3,600; adding it gives Rs. 27,600.", "Percentages", "Easy", tags=("salary", "increase"), roles=("software engineer", "analyst")),
    _question("qa-pct-02", "A value falls from 800 to 680. What is the percentage decrease?", ("12%", "15%", "18%", "20%"), 1, "The decrease is 120; 120 / 800 x 100 = 15%.", "Percentages", "Easy"),
    _question("qa-pct-03", "A price is raised by 20% and then discounted by 20%. What is the net change?", ("No change", "4% decrease", "4% increase", "8% decrease"), 1, "Using 100 as the starting price gives 120 x 0.8 = 96, a 4% decrease.", "Percentages", "Medium"),
    _question("qa-pct-04", "In a group, 40% are women. If there are 36 men, how many people are in the group?", ("54", "60", "64", "90"), 1, "Men are 60% of the group, so the total is 36 / 0.6 = 60.", "Percentages", "Medium"),
    _question("qa-pct-05", "A value is increased by 25%. By what percentage must the new value be reduced to return to the original?", ("16%", "20%", "25%", "33 1/3%"), 1, "After a 25% increase the value is 125; a reduction of 25/125 is 20%.", "Percentages", "Hard"),
    _question("qa-pl-01", "An item costing Rs. 750 is sold for Rs. 900. What is the profit percentage?", ("15%", "18%", "20%", "25%"), 2, "Profit is 150; 150 / 750 x 100 = 20%.", "Profit and Loss", "Easy"),
    _question("qa-pl-02", "A shopkeeper marks an item 25% above cost and gives a 10% discount. What is the profit percentage?", ("10%", "12.5%", "15%", "22.5%"), 1, "For cost 100, marked price is 125 and selling price is 112.5, so profit is 12.5%.", "Profit and Loss", "Medium"),
    _question("qa-ratio-01", "The ratio of two numbers is 3:5 and their sum is 64. What is the smaller number?", ("18", "24", "30", "40"), 1, "There are 8 equal parts; each is 8, so the smaller number is 3 x 8 = 24.", "Ratio and Proportion", "Easy"),
    _question("qa-ratio-02", "A sum is divided among A, B and C in the ratio 2:3:5. If C receives Rs. 1,500, what is the total sum?", ("Rs. 2,500", "Rs. 3,000", "Rs. 3,500", "Rs. 5,000"), 1, "Five parts equal 1,500, so one part is 300 and ten parts total 3,000.", "Ratio and Proportion", "Medium"),
    _question("qa-avg-01", "The average of 6, 10, 14 and x is 12. Find x.", ("14", "16", "18", "20"), 2, "The four values total 48; the known values total 30, so x = 18.", "Averages", "Easy"),
    _question("qa-avg-02", "The average of 5 consecutive integers is 18. What is the largest integer?", ("18", "19", "20", "21"), 2, "The middle integer is the average, 18; the sequence is 16 through 20.", "Averages", "Medium"),
    _question("qa-si-01", "Find the simple interest on Rs. 5,000 at 8% per year for 2 years.", ("Rs. 400", "Rs. 800", "Rs. 1,000", "Rs. 1,200"), 1, "Simple interest = 5,000 x 8 x 2 / 100 = Rs. 800.", "Simple Interest", "Easy"),
    _question("qa-si-02", "At 6% simple interest per year, how long will Rs. 4,000 take to earn Rs. 960 interest?", ("3 years", "4 years", "5 years", "6 years"), 1, "Time = 960 x 100 / (4,000 x 6) = 4 years.", "Simple Interest", "Medium"),
    _question("qa-ci-01", "What is the amount on Rs. 1,000 at 10% compound interest per year for 2 years?", ("Rs. 1,100", "Rs. 1,200", "Rs. 1,210", "Rs. 1,220"), 2, "Amount = 1,000 x 1.1 x 1.1 = Rs. 1,210.", "Compound Interest", "Medium"),
    _question("qa-ci-02", "At 10% compounded annually, what is the compound interest on Rs. 2,000 over 2 years?", ("Rs. 400", "Rs. 420", "Rs. 440", "Rs. 460"), 1, "The amount is 2,000 x 1.1^2 = 2,420; interest is Rs. 420.", "Compound Interest", "Hard"),
    _question("qa-work-01", "A can complete a task in 12 days and B in 6 days. How many days do they need working together?", ("3 days", "4 days", "6 days", "9 days"), 1, "Their combined rate is 1/12 + 1/6 = 1/4 of the task per day.", "Time and Work", "Easy"),
    _question("qa-work-02", "A completes a task in 10 days and B in 15 days. What fraction remains after they work together for 3 days?", ("1/5", "1/2", "3/5", "4/5"), 1, "Their daily rate is 1/10 + 1/15 = 1/6; in 3 days they complete 1/2.", "Time and Work", "Medium"),
    _question("qa-speed-01", "A vehicle travels 150 km in 3 hours. What is its average speed?", ("40 km/h", "45 km/h", "50 km/h", "55 km/h"), 2, "Average speed = distance / time = 150 / 3 = 50 km/h.", "Time, Speed and Distance", "Easy"),
    _question("qa-speed-02", "A person travels equal distances at 40 km/h and 60 km/h. What is the average speed for the whole journey?", ("45 km/h", "48 km/h", "50 km/h", "52 km/h"), 1, "For equal distances, average speed is 2ab/(a+b) = 4,800/100 = 48 km/h.", "Time, Speed and Distance", "Hard"),
    _question("qa-train-01", "A 120 m train passes a pole in 6 seconds. What is its speed in km/h?", ("60", "72", "80", "90"), 1, "Speed is 120/6 = 20 m/s; multiplying by 3.6 gives 72 km/h.", "Problems on Trains", "Medium"),
    _question("qa-train-02", "A 150 m train moving at 54 km/h passes a 250 m platform. How long does it take?", ("20 seconds", "24 seconds", "26 2/3 seconds", "30 seconds"), 2, "It covers 400 m at 15 m/s, taking 400/15 = 26 2/3 seconds.", "Problems on Trains", "Hard"),
    _question("qa-pipes-01", "A pipe fills a tank in 6 hours and a drain empties it in 12 hours. With both open, how long to fill an empty tank?", ("6 hours", "8 hours", "10 hours", "12 hours"), 3, "Net rate is 1/6 - 1/12 = 1/12 tank per hour.", "Pipes and Cisterns", "Medium"),
    _question("qa-number-01", "What is the remainder when 2^5 + 3^2 is divided by 7?", ("4", "5", "6", "0"), 2, "2^5 + 3^2 = 32 + 9 = 41; 41 divided by 7 leaves remainder 6.", "Number System", "Easy"),
    _question("qa-number-02", "How many positive divisors does 36 have?", ("6", "8", "9", "12"), 2, "36 = 2^2 x 3^2, so it has (2+1)(2+1) = 9 positive divisors.", "Number System", "Medium"),
    _question("qa-hcf-01", "Find the HCF of 48 and 72.", ("12", "18", "24", "36"), 2, "The greatest integer dividing both 48 and 72 is 24.", "HCF and LCM", "Easy"),
    _question("qa-hcf-02", "Two bells ring every 12 and 18 minutes. If they ring together now, after how many minutes will they next ring together?", ("24", "30", "36", "72"), 2, "They coincide after the LCM of 12 and 18, which is 36 minutes.", "HCF and LCM", "Medium"),
    _question("qa-prob-01", "A fair six-sided die is rolled once. What is the probability of getting an even number?", ("1/6", "1/3", "1/2", "2/3"), 2, "Three of the six equally likely outcomes are even, so the probability is 3/6 = 1/2.", "Probability", "Easy"),
    _question("qa-prob-02", "A bag has 3 red and 2 blue balls. Two balls are drawn without replacement. What is the probability both are red?", ("1/5", "3/10", "2/5", "1/2"), 1, "The probability is 3/5 x 2/4 = 3/10.", "Probability", "Hard"),
    _question("qa-perm-01", "How many different arrangements can be made using all the letters in CAT?", ("3", "6", "9", "12"), 1, "The three distinct letters can be arranged in 3! = 6 ways.", "Permutation and Combination", "Easy", roles=("software engineer", "data analyst")),
    _question("qa-perm-02", "How many committees of 2 can be selected from 6 people?", ("12", "15", "30", "36"), 1, "Order does not matter, so the count is 6C2 = 6 x 5 / 2 = 15.", "Permutation and Combination", "Medium"),
    _question("qa-mix-01", "A 10 L mixture contains milk and water in the ratio 4:1. How much water must be added to make the ratio 2:1?", ("1 L", "2 L", "3 L", "4 L"), 1, "The mixture has 8 L milk and 2 L water; 4 L water gives an 8:4 ratio.", "Mixtures and Allegations", "Medium"),
    _question("qa-mix-02", "Rice costing Rs. 40/kg is mixed with rice costing Rs. 60/kg to obtain a mixture worth Rs. 45/kg. What is the ratio of cheaper to dearer rice?", ("1:3", "2:1", "3:1", "4:1"), 2, "By allegation, the cheaper-to-dearer ratio is (60-45):(45-40) = 15:5 = 3:1.", "Mixtures and Allegations", "Hard"),
    _question("qa-ages-01", "A parent is 36 years old and a child is 12. In how many years will the parent be twice the child's age?", ("8", "10", "12", "14"), 2, "36+x = 2(12+x), so x = 12 years.", "Ages", "Easy"),
    _question("qa-ages-02", "The present ages of A and B are in the ratio 4:3. In 6 years their ages will total 54. What is A's present age?", ("20", "24", "28", "32"), 1, "Their current total is 54-12 = 42; seven ratio parts equal 42, so A is 4 x 6 = 24.", "Ages", "Medium"),

    _question("lr-series-01", "What number comes next: 4, 9, 16, 25, 36, ...?", ("42", "45", "49", "64"), 2, "The sequence contains consecutive squares: 2^2, 3^2, 4^2, 5^2, 6^2; next is 7^2 = 49.", "Number Series", "Easy", category="Logical Reasoning"),
    _question("lr-series-02", "Find the next term: 3, 7, 15, 31, ...", ("47", "55", "61", "63"), 3, "Each term is multiplied by 2 and increased by 1; 31 x 2 + 1 = 63.", "Number Series", "Medium", category="Logical Reasoning"),
    _question("lr-letter-01", "What letter comes next: A, C, F, J, O, ...?", ("T", "U", "V", "W"), 1, "The letter positions increase by 2, 3, 4, 5; the next jump is 6, giving U.", "Letter Series", "Medium", category="Logical Reasoning"),
    _question("lr-code-01", "In a code, each letter is replaced by the next letter in the alphabet. How is MATH written?", ("NBUG", "NBUI", "LZSG", "NATH"), 1, "Move each letter forward by one: M→N, A→B, T→U, H→I.", "Coding-Decoding", "Easy", category="Logical Reasoning"),
    _question("lr-code-02", "If each letter is shifted back by one, how is LION written?", ("KHNM", "KJPM", "MJPO", "KHON"), 0, "Shifting each letter back one place gives L→K, I→H, O→N, N→M.", "Coding-Decoding", "Medium", category="Logical Reasoning"),
    _question("lr-blood-01", "Riya says, “He is the son of my mother's only daughter.” How is the boy related to Riya?", ("Brother", "Son", "Nephew", "Cousin"), 1, "Riya is her mother's only daughter, so that woman's son is Riya's son.", "Blood Relations", "Easy", category="Logical Reasoning"),
    _question("lr-blood-02", "A is the brother of B. B is the mother of C. How is A related to C?", ("Paternal uncle", "Maternal uncle", "Grandfather", "Cousin"), 1, "A is the brother of C's mother, so A is C's maternal uncle.", "Blood Relations", "Medium", category="Logical Reasoning"),
    _question("lr-directions-01", "Maya walks 5 km north, then 3 km east. In which direction is she from her starting point?", ("North", "East", "North-east", "South-east"), 2, "She is north and east of the start, so the direction is north-east.", "Directions", "Easy", category="Logical Reasoning"),
    _question("lr-directions-02", "A person faces east, turns left, then turns around. Which direction is the person facing?", ("North", "South", "East", "West"), 1, "Facing east, a left turn points north; turning around points south.", "Directions", "Medium", category="Logical Reasoning"),
    _question("lr-syllogism-01", "Statements: All analysts are graduates. Some graduates are artists. Which conclusion follows?", ("All artists are analysts", "Some analysts are artists", "All analysts are graduates", "No graduate is an artist"), 2, "The first conclusion restates a given statement. The overlap of analysts and artists is not guaranteed.", "Syllogisms", "Medium", category="Logical Reasoning"),
    _question("lr-syllogism-02", "Statements: No laptops are tablets. All tablets are portable. Which conclusion must be true?", ("No laptops are portable", "No tablets are laptops", "All portable items are tablets", "Some laptops are tablets"), 1, "If no laptop is a tablet, then no tablet is a laptop; the other conclusions do not follow.", "Syllogisms", "Hard", category="Logical Reasoning"),
    _question("lr-conclusion-01", "Statement: The college extended library hours during exam week. Which conclusion is most reasonable?", ("Every student studies at night", "The library expects higher study demand", "All exams are difficult", "The college cancelled classes"), 1, "Extending hours most directly suggests the college expects more demand for study space.", "Statements and Conclusions", "Medium", category="Logical Reasoning"),
    _question("lr-seating-01", "Four people P, Q, R and S sit in a row. P is left of Q, R is right of Q, and S is left of P. Who is second from the left?", ("P", "Q", "R", "S"), 0, "The constraints give the order S, P, Q, R; P is second from the left.", "Seating Arrangement", "Medium", category="Logical Reasoning"),
    _question("lr-puzzle-01", "Three tasks A, B and C are scheduled in a row. A is before B, and C is after B. What is the order?", ("A, B, C", "A, C, B", "B, A, C", "C, B, A"), 0, "A must precede B and C must follow B, giving A, B, C.", "Puzzles", "Easy", category="Logical Reasoning"),
    _question("lr-puzzle-02", "Four meetings W, X, Y and Z are scheduled Monday to Thursday, one per day. W is Monday, X is before Z, and Y is Thursday. Which day is X?", ("Monday", "Tuesday", "Wednesday", "Thursday"), 1, "Monday is W and Thursday is Y; X and Z occupy Tuesday and Wednesday in that order.", "Puzzles", "Hard", category="Logical Reasoning"),
    _question("lr-suff-01", "What is x? (1) x + y = 10. (2) y = 4.", ("Statement 1 alone is sufficient", "Statement 2 alone is sufficient", "Both statements together are sufficient", "Either statement alone is sufficient"), 2, "Together, x + 4 = 10, so x = 6. Neither statement alone fixes x.", "Data Sufficiency", "Medium", category="Logical Reasoning"),
    _question("lr-suff-02", "Is integer n even? (1) n is divisible by 4. (2) n is divisible by 6.", ("Statement 1 alone is sufficient", "Statement 2 alone is sufficient", "Both statements together are sufficient", "Neither statement is sufficient"), 0, "Every integer divisible by 4 is even, so statement 1 alone answers yes.", "Data Sufficiency", "Hard", category="Logical Reasoning"),

    _question("va-grammar-01", "Choose the grammatically correct sentence.", ("Each of the applicants have submitted a resume.", "Each of the applicants has submitted a resume.", "Each applicants has submitted a resume.", "Each of applicant have submitted a resume."), 1, "“Each” is singular and takes the singular verb “has.”", "Grammar", "Easy", category="Verbal Ability"),
    _question("va-grammar-02", "Choose the correct sentence.", ("Neither the manager nor the employees was available.", "Neither the manager nor the employees were available.", "Neither manager or employees were available.", "Neither the manager nor employees is available."), 1, "With “neither...nor,” the verb agrees with the nearer subject, “employees,” which is plural.", "Grammar", "Hard", category="Verbal Ability"),
    _question("va-correction-01", "Choose the best correction: “She is senior than her colleague.”", ("She is more senior than her colleague.", "She is senior to her colleague.", "She is most senior than her colleague.", "She is senior from her colleague."), 1, "“Senior” is conventionally followed by “to,” not “than.”", "Sentence Correction", "Medium", category="Verbal Ability"),
    _question("va-vocab-01", "Choose the closest meaning of “concise.”", ("Brief and clear", "Uncertain", "Highly detailed", "Unrelated"), 0, "“Concise” means expressing something briefly and clearly.", "Vocabulary", "Easy", category="Verbal Ability"),
    _question("va-syn-01", "Choose the antonym of “scarce.”", ("Rare", "Limited", "Abundant", "Insufficient"), 2, "“Abundant” means plentiful, the opposite of “scarce.”", "Synonyms and Antonyms", "Medium", category="Verbal Ability"),
    _question("va-reading-01", "A team tested two onboarding guides with new users. Completion rose from 70% to 84% with the shorter guide, while support requests stayed level. What is the best-supported conclusion?", ("The shorter guide improved completion in this test", "The shorter guide eliminated all user confusion", "Every user prefers short documents", "Support requests decreased"), 0, "The data shows higher completion and unchanged support requests; it does not establish the broader claims.", "Reading Comprehension", "Medium", category="Verbal Ability", seconds=75, roles=("product manager", "customer success")),
    _question("va-order-01", "Arrange these sentences: (1) Finally, the team reviewed the results. (2) First, it defined the problem. (3) It then ran a small experiment.", ("2, 3, 1", "1, 2, 3", "3, 2, 1", "2, 1, 3"), 0, "The sequence markers “First” and “Finally” place the problem definition first and review last.", "Sentence Arrangement", "Medium", category="Verbal Ability"),
    _question("va-grammar-03", "Choose the correct sentence.", ("The data shows a steady improvement.", "The data show a steady improvement.", "The datas show a steady improvement.", "The data showing a steady improvement."), 1, "In formal usage “data” is plural, so it takes “show.”", "Grammar", "Medium", category="Verbal Ability"),
    _question("va-grammar-04", "Choose the correct sentence.", ("If I had known about the change, I would have informed you.", "If I knew about the change, I would have informed you.", "If I would know about the change, I informed you.", "If I have known about the change, I would inform you."), 0, "A past unreal condition uses past perfect in the if-clause and “would have” in the result clause.", "Grammar", "Medium", category="Verbal Ability"),
    _question("va-vocab-02", "Choose the closest meaning of “mitigate.”", ("Make less severe", "Make permanent", "Measure precisely", "Make more complex"), 0, "To mitigate means to reduce the severity or impact of something.", "Vocabulary", "Hard", category="Verbal Ability"),
    _question("va-reading-02", "A pilot let employees choose either remote or office days. Output stayed stable, but employees reported fewer interruptions. Which statement is supported?", ("The pilot reduced reported interruptions without reducing output", "The pilot increased output", "All employees chose remote work", "The pilot reduced working hours"), 0, "The passage reports stable output and fewer reported interruptions only.", "Reading Comprehension", "Easy", category="Verbal Ability", seconds=75),
    _question("va-order-02", "Arrange the steps logically: (1) Submit the form. (2) Review the required fields. (3) Receive a confirmation.", ("1, 2, 3", "2, 1, 3", "3, 1, 2", "2, 3, 1"), 1, "Reviewing fields comes before submission; confirmation follows submission.", "Sentence Arrangement", "Hard", category="Verbal Ability"),
    _question("va-correction-02", "Choose the best correction: “Despite of the delay, the team finished.”", ("Despite the delay, the team finished.", "Despite the delay, but the team finished.", "In despite the delay, the team finished.", "Despite of delay, the team finished."), 0, "“Despite” is followed directly by a noun phrase; “of” is not used after it.", "Sentence Correction", "Easy", category="Verbal Ability"),
    _question("va-correction-03", "Choose the correct completion: “The team delivered the report ___ time.”", ("in", "on", "at", "by"), 1, "The standard expression meaning as scheduled is “on time.”", "Sentence Correction", "Medium", category="Verbal Ability"),

    _question("nv-pattern-01", "Which symbol comes next: ▲, ■, ▲, ■, ▲, ...?", ("▲", "■", "●", "◆"), 1, "The sequence alternates between a triangle and a square; the next symbol is a square.", "Pattern-based Reasoning", "Easy", category="Non-verbal Reasoning"),
    _question("nv-pattern-02", "A shape sequence has 1, 2, 4, 8 shaded circles in successive figures. How many should the next figure have?", ("10", "12", "14", "16"), 3, "The number of shaded circles doubles each time; 8 x 2 = 16.", "Figure-based Reasoning", "Medium", category="Non-verbal Reasoning"),
    _question("nv-analogy-01", "Complete the analogy: triangle is to 3 sides as hexagon is to ...", ("5 sides", "6 sides", "7 sides", "8 sides"), 1, "A hexagon has six sides.", "Analogy", "Easy", category="Non-verbal Reasoning"),
    _question("nv-class-01", "Which item does not belong with the others?", ("Circle", "Square", "Triangle", "Cube"), 3, "A cube is three-dimensional; the other shapes listed are two-dimensional.", "Classification", "Medium", category="Non-verbal Reasoning"),
    _question("nv-analogy-02", "Complete the analogy: small square, medium square, large square, ...", ("Small circle", "Medium circle", "Extra-large square", "Large triangle"), 2, "The shape remains a square while its size increases at each step.", "Analogy", "Hard", category="Non-verbal Reasoning"),
    _question("nv-class-02", "Which pair differs from the others?", ("▲ ▲", "■ ■", "● ●", "▲ ■"), 3, "The first three pairs contain matching shapes; the last pair contains different shapes.", "Classification", "Easy", category="Non-verbal Reasoning"),
]


def get_question(question_id: str) -> QuestionDefinition | None:
    return next((question for question in QUESTION_BANK if question["id"] == question_id), None)
