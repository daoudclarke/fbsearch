import pstats
p = pstats.Stats('profile_output')
p.strip_dirs().sort_stats('cumulative').print_stats()
