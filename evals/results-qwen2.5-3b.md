# Evaluation results

Chat model `qwen2.5:3b`, embeddings `nomic-embed-text`, top-k = 4. 34 answerable + 6 out-of-scope questions.

## Retrieval

| Mode | Section hit@4 | Section MRR | Document hit@4 | Missed |
|---|---|---|---|---|
| bm25 | 94% | 0.82 | 97% | q13, q34 |
| vector | 97% | 0.89 | 97% | q22 |
| hybrid | 94% | 0.89 | 100% | q13, q34 |
| hybrid+rewrite | 94% | 0.89 | 100% | q22, q34 |

## Answers (retrieval mode `hybrid+rewrite`)

| Metric | Value |
|---|---|
| Answer accuracy (required facts present) | 82% (28/34) |
| Answers with a citation | 91% |
| Citation points to the right policy section | 82% |
| False refusals on answerable questions | 3/34 |
| Refusal accuracy on out-of-scope questions | 100% (6/6) |
| Median latency | 13.7 s |

## Per-question results

| ID | Question | Pass | Answer |
|---|---|---|---|
| q01 | How old do I need to be to apply for a loan? | ✅ | You need to be at least 21 years old to apply for a loan. |
| q02 | I am salaried. What is the minimum monthly salary needed? | ✅ | The minimum monthly salary needed as a salaried applicant is Rs 25,000. |
| q03 | What minimum income does a self-employed person need to show? | ✅ | A self-employed person needs to show a minimum average monthly income of Rs 40,000. |
| q04 | What is the lowest credit score you accept? | ✅ | The lowest credit score you accept is 650. Any score below this will result in an automatic decline. |
| q05 | My CIBIL score is 670. Can I still get a loan? | ✅ | Yes, you can still get a loan with a CIBIL score of 670. You would need a co-applicant with a score of 720 or higher to qualify. [1] |
| q06 | I have never taken a loan or credit card before. How much can I borrow? | ❌ | I couldn't find this in the Northwind Credit policy documents. Please contact support. |
| q07 | How long must I have worked at my current company? | ✅ | You must have worked at your current company for at least 6 months. [1] |
| q08 | I earn 1.5 lakh a month. What share of my income can go to EMIs? | ✅ | For applicants earning more than Rs 1,00,000 per month, the FOIR limit is relaxed to 60%. Therefore, you can allocate up to 60% of your income to EMIs. |
| q09 | What is the biggest personal loan I can get? | ✅ | The biggest personal loan you can get is Rs 15,00,000. |
| q10 | What is the longest repayment period for a business term loan? | ✅ | The longest repayment period for a business term loan is 48 months. [1] |
| q11 | What percentage of an invoice can supplier financing cover? | ✅ | Supplier invoice financing covers up to 80% of the invoice value. [1] |
| q12 | How much markup is charged on a markup loan? | ✅ | The markup ranges from 1.5% to 3% per month and is fixed at the time of approval and charged on the financed amount. |
| q13 | Is there a limit on loan amount for the riskiest borrowers? | ✅ | Yes, there is a limit on loan amount for the riskiest borrowers (Grade E). They are capped at 50% of the maximum loan amount for the product. |
| q14 | After I sign the agreement, how soon will I get the money? | ✅ | You will get the money within 2 business days after signing the agreement. Requests completed before 3:00 PM IST are processed the same day, and those completed after are processed the next business day. |
| q15 | Until what time can I complete my request to get same-day disbursement? | ✅ | You can complete your request to get same-day disbursement by 3:00 PM IST. |
| q16 | How do you check that my bank account is correct before sending money? | ✅ | Your bank account is verified through a penny-drop test, which deposits Rs 1 into the account to confirm the account holder's name matches the borrower or approved supplier. |
| q17 | What happens if the money transfer to my account fails? | ✅ | If the money transfer to your account fails due to an invalid account or a bank outage, the system will retry the disbursement up to 3 times at 2-hour intervals. After 3 failed attempts, the disbursement will be moved to manual review by the operations team, and you will be notified by SMS and email. |
| q18 | Above what amount does a payout need two approvers? | ❌ | [2] |
| q19 | Can supplier invoice financing be paid into the merchant's own account? | ❌ | I couldn't find this in the Northwind Credit policy documents. Please contact support. |
| q20 | What processing fee do you charge? | ✅ | We charge a processing fee of 2% of the loan amount, with a minimum of Rs 1,999. |
| q21 | What is the penalty if my auto-debit bounces? | ✅ | If your auto-debit fails because of insufficient funds, you will be charged a bounce charge of Rs 500. |
| q22 | When am I allowed to close my loan early? | ❌ | [2] You are allowed to close your loan early by making a single payment of the financed amount plus markup on the due date. Early repayment is allowed at any time, and the markup is then charged only for the days actually used, subject to a minimum of 15 days. |
| q23 | How much do I pay to foreclose a fixed-rate loan? | ❌ | I couldn't find this in the Northwind Credit policy documents. Please contact support. |
| q24 | Which dates can I pick for my EMI? | ✅ | You can choose your EMI date as the 5th, 10th, or 15th of each month. |
| q25 | If I repay a markup loan early, is the markup reduced? | ✅ | Yes, if you repay a markup loan early, the markup is reduced to only charge for the days actually used, with a minimum of 15 days. |
| q26 | How many months of payslips do salaried applicants submit? | ✅ | Salaried applicants submit payslips for the last 3 months. [1] |
| q27 | For how many months of GST returns does a business need to provide? | ✅ | A business needs to provide GST returns for the last 12 months. [1] |
| q28 | How often do high-risk customers have to redo KYC? | ✅ | High-risk customers have to redo KYC every 2 years. |
| q29 | What documents does a supplier need to give before receiving invoice financing? | ✅ | A supplier needs to provide its GSTIN, PAN, and a cancelled cheque or bank letter before receiving invoice financing. |
| q30 | At what times are recovery agents allowed to call me? | ✅ | Recovery agents are allowed to call you between 8:00 AM and 7:00 PM. |
| q31 | I lost my job. Can I pause my EMIs for a while? | ✅ | Yes, you can request a moratorium of up to 3 months. Interest will continue to accrue during this time. [1] |
| q32 | After how many days overdue does a loan become an NPA? | ✅ | A loan becomes an NPA after 90 days past due (DPD). |
| q33 | How long does the grievance officer have to resolve my complaint? | ✅ | The grievance officer has 30 days to resolve your complaint. [1] |
| q34 | Can I close my loan early, and what will it cost? | ❌ | Yes, you can close your loan early. For Supplier Invoice Financing, there is no cost for early repayment. For other loans, there is a processing fee of 2% of the loan amount, subject to a minimum of Rs 1,999, which will be deducted from the disbursed amount. |
| u01 | What is the interest rate on a home loan? | ✅ | I couldn't find this in the Northwind Credit policy documents. Please contact support. |
| u02 | Does Northwind Credit offer credit cards? | ✅ | I couldn't find this in the Northwind Credit policy documents. Please contact support. |
| u03 | Who is the CEO of Northwind Credit? | ✅ | I couldn't find this in the Northwind Credit policy documents. Please contact support. |
| u04 | Can I pay my EMI using Bitcoin? | ✅ | I couldn't find this in the Northwind Credit policy documents. Please contact support. |
| u05 | What is the current RBI repo rate? | ✅ | I couldn't find this in the Northwind Credit policy documents. Please contact support. |
| u06 | What is the per-gram rate for a gold loan? | ✅ | I couldn't find this in the Northwind Credit policy documents. Please contact support. |
