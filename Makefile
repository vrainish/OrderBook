SHELL = /usr/bin/tcsh
	

test:
	time ./Pricer.py 200 < in/pricer.in  > out.200
	diff out.200 out/pricer.out.200
	rm out.200
	time ./Pricer.py 1 < in/pricer.in  > out.1
	diff out.1 out/pricer.out.1
	rm out.1
	time ./Pricer.py 10000 < in/pricer.in  > out.10000
	diff out.10000 out/pricer.out.10000
	rm out.10000
ftest:
	@echo "\nPricer 200"
	@time ./Pricer.py 200 < in/pricer.in  > out.200
	@time ./Pricer.py 200 < in/pricer.in  > out.200
	@time ./Pricer.py 200 < in/pricer.in  > out.200
	@rm out.200
	@echo "\nPricer 1"
	@time ./Pricer.py 1 < in/pricer.in  > out.1
	@time ./Pricer.py 1 < in/pricer.in  > out.1
	@time ./Pricer.py 1 < in/pricer.in  > out.1
	@rm out.1
	@echo "\nPricer 10000"
	@time ./Pricer.py 10000 < in/pricer.in  > out.10000
	@time ./Pricer.py 10000 < in/pricer.in  > out.10000
	@time ./Pricer.py 10000 < in/pricer.in  > out.10000
	@rm out.10000
s_test:
	time ./SimplePricer.py 200 < in/pricer.in  > out.200
	diff out.200 out/pricer.out.200
	rm out.200
	time ./SimplePricer.py 1 < in/pricer.in  > out.1
	diff out.1 out/pricer.out.1
	rm out.1
	time ./SimplePricer.py 10000 < in/pricer.in  > out.10000
	diff out.10000 out/pricer.out.10000
	rm out.10000
