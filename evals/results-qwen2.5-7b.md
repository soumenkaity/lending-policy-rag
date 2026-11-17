# Evaluation results

Chat model `qwen2.5:7b`, embeddings `nomic-embed-text`, top-k = 4. 34 answerable + 6 out-of-scope questions.

## Retrieval

| Mode | Section hit@4 | Section MRR | Document hit@4 | Missed |
|---|---|---|---|---|
| bm25 | 94% | 0.82 | 97% | q13, q34 |
| vector | 97% | 0.89 | 97% | q22 |
| hybrid | 94% | 0.89 | 100% | q13, q34 |
| hybrid+rewrite | 100% | 0.96 | 100% | - |

## Answers (retrieval mode `hybrid+rewrite`)

| Metric | Value |
|---|---|
| Answer accuracy (required facts present) | 100% (34/34) |
| Answers with a citation | 100% |
| Citation points to the right policy section | 100% |
| False refusals on answerable questions | 0/34 |
| Refusal accuracy on out-of-scope questions | 100% (6/6) |
| Median latency | 26.5 s |

## Per-question results

| ID | Question | Pass | Answer |
|---|---|---|---|
| q01 | How old do I need to be to apply for a loan? | ✅ | You must be at least 21 years old to apply for a loan. For salaried applicants, your age at loan maturity should not exceed 60 years, while for self-employed applicants, it should not exceed 65 years. [1] |
| q02 | I am salaried. What is the minimum monthly salary needed? | ✅ | As a salaried applicant, you need a minimum net monthly income of Rs 25,000. [1] |
| q03 | What minimum income does a self-employed person need to show? | ✅ | A self-employed person must show a minimum average monthly income of Rs 40,000, calculated from the last two years of income tax returns. [1] |
| q04 | What is the lowest credit score you accept? | ✅ | The lowest credit score accepted by Northwind Credit is 700. [1] |
| q05 | My CIBIL score is 670. Can I still get a loan? | ✅ | Yes, you may be eligible for a loan, but you will need a co-applicant with a credit score of 720 or higher to be approved. [1] |
| q06 | I have never taken a loan or credit card before. How much can I borrow? | ✅ | You can borrow up to Rs 1,00,000 as a new credit applicant with no credit history. [1] |
| q07 | How long must I have worked at my current company? | ✅ | You must have worked at your current employer for at least 6 months. [1] |
| q08 | I earn 1.5 lakh a month. What share of my income can go to EMIs? | ✅ | Since you earn Rs 1.5 lakh a month, which is more than Rs 1,00,000, the fixed obligation to income ratio (FOIR) limit for your proposed EMIs can be up to 60% of your net monthly income. [1] |
| q09 | What is the biggest personal loan I can get? | ✅ | The biggest personal loan you can get is Rs 15,00,000. [1] |
| q10 | What is the longest repayment period for a business term loan? | ✅ | The longest repayment period for a business term loan is 48 months. [1] |
| q11 | What percentage of an invoice can supplier financing cover? | ✅ | Supplier financing can cover up to 80% of the invoice value. [1] |
| q12 | How much markup is charged on a markup loan? | ✅ | The markup charged on a markup loan ranges from 1.5% to 3% per month, fixed at the time of approval and charged on the financed amount. [1] |
| q13 | Is there a limit on loan amount for the riskiest borrowers? | ✅ | Yes, for the riskiest borrowers (risk grade E), there is a limit on the loan amount, which is capped at 50% of the maximum loan amount for the product. [4] |
| q14 | After I sign the agreement, how soon will I get the money? | ✅ | You will receive the money within 2 business days after signing the agreement. If you complete your request before 3:00 PM IST, it will be processed on the same day. Otherwise, it will be processed on the next business day. [1] |
| q15 | Until what time can I complete my request to get same-day disbursement? | ✅ | You can complete your request to get a same-day disbursement until 3:00 PM IST. [1] |
| q16 | How do you check that my bank account is correct before sending money? | ✅ | Your bank account is verified through a penny-drop test, where Rs 1 is deposited into the account to confirm that the account holder name matches the borrower or the approved supplier. [1] |
| q17 | What happens if the money transfer to my account fails? | ✅ | If the money transfer to your account fails, the system will retry up to 3 times at 2-hour intervals. If it fails 3 times, the disbursement will be reviewed manually by the operations team, and you will be notified by SMS and email. [1] |
| q18 | Above what amount does a payout need two approvers? | ✅ | A payout needs two approvers for amounts above Rs 25,00,000. [1] |
| q19 | Can supplier invoice financing be paid into the merchant's own account? | ✅ | No, supplier invoice financing cannot be paid into the merchant's own account; it is always disbursed directly to the approved supplier's verified bank account. [1] |
| q20 | What processing fee do you charge? | ✅ | We charge a processing fee of 2% of the loan amount, with a minimum of Rs 1,999, and GST at 18% is applied to this fee. [1] |
| q21 | What is the penalty if my auto-debit bounces? | ✅ | A bounce charge of Rs 500 is applied each time an auto-debit fails due to insufficient funds. [1] |
| q22 | When am I allowed to close my loan early? | ✅ | You are allowed to close your loan early after making 6 EMIs, but part-prepayment is limited to 25% of the outstanding principal once per financial year and carries no charge. Foreclosure, however, incurs a charge of 4% of the outstanding principal. [1] |
| q23 | How much do I pay to foreclose a fixed-rate loan? | ✅ | You pay 4% of the outstanding principal to foreclose a fixed-rate loan. [1] |
| q24 | Which dates can I pick for my EMI? | ✅ | You can choose the 5th, 10th, or 15th of each month as your EMI date. [1] |
| q25 | If I repay a markup loan early, is the markup reduced? | ✅ | Yes, if you repay a markup loan early, the markup is reduced to only cover the days actually used, but it is subject to a minimum of 15 days. [1] |
| q26 | How many months of payslips do salaried applicants submit? | ✅ | Salaried applicants submit salary slips for the last 3 months. [1] |
| q27 | For how many months of GST returns does a business need to provide? | ✅ | A business needs to provide GST returns for the last 12 months. [1] |
| q28 | How often do high-risk customers have to redo KYC? | ✅ | High-risk customers have to redo KYC every 2 years. [1] |
| q29 | What documents does a supplier need to give before receiving invoice financing? | ✅ | A supplier needs to provide its GSTIN, PAN, and a cancelled cheque or bank letter before receiving invoice financing. Additionally, its bank account must pass the penny-drop test. [1] |
| q30 | At what times are recovery agents allowed to call me? | ✅ | Recovery agents are allowed to call you between 8:00 AM and 7:00 PM. [1] |
| q31 | I lost my job. Can I pause my EMIs for a while? | ✅ | Yes, you can pause your EMIs for up to 3 months if you face genuine financial hardship due to job loss. However, interest will continue to accrue during this period and will be added to your outstanding principal. You are entitled to only one such moratorium during the loan tenure. [1] |
| q32 | After how many days overdue does a loan become an NPA? | ✅ | A loan becomes an NPA after 91 days overdue. [1] |
| q33 | How long does the grievance officer have to resolve my complaint? | ✅ | The Grievance Redressal Officer must resolve your complaint within 30 days. [1] |
| q34 | Can I close my loan early, and what will it cost? | ✅ | Yes, you can close your loan early, but you must first make 6 EMIs. For partial prepayment, you can pay up to 25% of the outstanding principal once per financial year with no additional charge. Full foreclosure will incur a charge of 4% of the outstanding principal. [4] |
| u01 | What is the interest rate on a home loan? | ✅ | I couldn't find this in the Northwind Credit policy documents. Please contact support. |
| u02 | Does Northwind Credit offer credit cards? | ✅ | I couldn't find this in the Northwind Credit policy documents. Please contact support. |
| u03 | Who is the CEO of Northwind Credit? | ✅ | I couldn't find this in the Northwind Credit policy documents. Please contact support. |
| u04 | Can I pay my EMI using Bitcoin? | ✅ | I couldn't find this in the Northwind Credit policy documents. Please contact support. |
| u05 | What is the current RBI repo rate? | ✅ | I couldn't find this in the Northwind Credit policy documents. Please contact support. |
| u06 | What is the per-gram rate for a gold loan? | ✅ | I couldn't find this in the Northwind Credit policy documents. Please contact support. |
