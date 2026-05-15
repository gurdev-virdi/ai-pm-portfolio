============================================================
TOKENIZATION EXAMPLES
============================================================

Text: 'Hello'
  Characters: 5
  Tokens:     1
  Ratio:      5.0 chars/token
  Breakdown:  ['Hello']

Text: 'Hello, how are you?'
  Characters: 19
  Tokens:     6
  Ratio:      3.2 chars/token
  Breakdown:  ['Hello', ',', ' how', ' are', ' you', '?']

Text: 'The quick brown fox jumps over the lazy dog'
  Characters: 43
  Tokens:     9
  Ratio:      4.8 chars/token
  Breakdown:  ['The', ' quick', ' brown', ' fox', ' jumps', ' over', ' the', ' lazy', ' dog']

Text: 'Retrieval-Augmented Generation (RAG) is a technique that combines information retrieval with language model generation.'
  Characters: 119
  Tokens:     21
  Ratio:      5.7 chars/token
  Breakdown:  ['Retr', 'ieval', '-Aug', 'mented', ' Generation', ' (', 'R', 'AG', ')', ' is', ' a', ' technique', ' that', ' combines', ' information', ' retrieval', ' with', ' language', ' model', ' generation', '.']

Text: 'こんにちは世界'
  Characters: 7
  Tokens:     2
  Ratio:      3.5 chars/token
  Breakdown:  ['こんにちは', '世界']

============================================================
MODEL PRICING COMPARISON
============================================================
Model                    Input/1M  Output/1M    Context
-------------------------------------------------------
gpt-4o                 $    2.50 $   10.00   128,000
gpt-4o-mini            $    0.15 $    0.60   128,000
claude-sonnet-4        $    3.00 $   15.00   200,000
claude-haiku-3.5       $    0.80 $    4.00   200,000
gemini-2.0-flash       $    0.10 $    0.40 1,000,000
llama-3.2-local        $    0.00 $    0.00   128,000


============================================================
SCENARIO: Smart Reply Feature (1M users)
============================================================

Assumptions: 500 input tokens, 150 output tokens, 5x/day/user
Total monthly requests: 150,000,000

Model                    Monthly Cost    $/Request    $/User/Mo
--------------------------------------------------------------
llama-3.2-local        $        0.00 $   0.00000 $    0.0000
gemini-2.0-flash       $   16,500.00 $   0.00011 $    0.0165
gpt-4o-mini            $   24,750.00 $   0.00016 $    0.0248
claude-haiku-3.5       $  150,000.00 $   0.00100 $    0.1500
gpt-4o                 $  412,500.00 $   0.00275 $    0.4125
claude-sonnet-4        $  562,500.00 $   0.00375 $    0.5625

============================================================
COST OPTIMIZATION: TIERED MODEL STRATEGY
============================================================

Strategy: Route requests by complexity, not one-model-fits-all.

  Simple queries (60%): → gpt-4o-mini or gemini-flash
    e.g., "Thanks, sounds good!" auto-reply
    
  Medium queries (30%): → gpt-4o or claude-haiku
    e.g., Meeting reschedule reply with context
    
  Complex queries (10%): → claude-sonnet or gpt-4o
    e.g., Detailed project update email

  All Claude Sonnet:   $  562,500.00/month
  Tiered approach:     $  116,100.00/month
  Monthly savings:     $  446,400.00 (79% reduction)
  Annual savings:      $5,356,800.00