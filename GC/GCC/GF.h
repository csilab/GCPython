#pragma once
class GF
{
public:
	GF(int mlen, int lengthExtension);
	~GF();
	int numBlock;
	int blockLength;
	long gf;
	long gfMinus2;
	int mlen;
	long gfdiv(long den, long num);
	void toString();
private:
	bool isPrime(long num);
	long nextPrime(long num);
	void setDem(int lengthExtension);
};

