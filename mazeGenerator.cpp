#include <iostream>
#include <string>
#include <vector>
#include <deque>
#include <stack>
#include <mem.h>
#include <algorithm>

#define I_WANNA_DEBUG 0

::std::vector<void *> pool;

void *getSpace(size_t size)
{
    void *out = malloc(size);
    pool.push_back(out);
    return out;
}

void freeSpace()
{
    for (::std::vector<void *>::iterator it = pool.begin(); it != pool.end(); it++)
    {
        free(*it);
    }
    pool.clear();
}

struct Ticker
{
    ::std::vector<int> data;
    unsigned int dimension;
    Ticker()
    {
        this->dimension = 0;
    }

    // Ticker(const Ticker &ticker)
    // {
    //     for (::std::vector<int>::iterator it = ticker.data.begin(); it != ticker.data.end(); it++)
    //     {
    //         this->data.push_back(*it);
    //     }
    //     this->dimension = this->data.size();
    // }

    Ticker(const Ticker &ticker)
    {
        for (int i = 0; i < ticker.dimension; i++)
        {
            this->data.push_back(ticker.data[i]);
        }
        this->dimension = this->data.size();
    }

    Ticker(int *address, int size)
    {
        for (int i = 0; i < size; i++)
        {
            this->data.push_back(address[i]);
        }
        this->dimension = this->data.size();
    }

    void _print_me()
    {
#if I_WANNA_DEBUG
        ::std::string s;
        for (::std::vector<int>::iterator it = this->data.begin();;)
        {
            s += ::std::to_string(*it);
            if (++it == this->data.end())
                break;
            s += ", ";
        }
        printf("Ticker{dim=%d, size=%d, coord=(%s)}\n",
               this->dimension, this->data.size(), s.c_str());
#endif
    }

    int operator[](int i)
    {
        return this->data[i];
    }

    Ticker operator+(Ticker &ticker)
    {
        Ticker out;
        for (int i = 0; i < this->dimension; i++)
        {
            out.data.push_back(this->data[i] + ticker.data[i]);
        }
        out.dimension = this->dimension;
        return out;
    }

    bool operator==(Ticker &ticker)
    {
        if (this->dimension == 0 || ticker.dimension == 0 || this->dimension != ticker.dimension)
        {
            return false;
        }
        for (int i = 0; i < this->dimension; i++)
        {
            if (this->data[i] != ticker.data[i])
            {
                return false;
            }
        }
        return true;
    }
};

struct MazeGenerator
{
    unsigned char *data;
    Ticker shape;
    unsigned int dimension = 4;
    ::std::vector<Ticker> directions;
    ::std::stack<Ticker> exploreHistory;
    bool result = false;
    ::std::deque<Ticker> funcDeque; // ticker valid->call explore; else:call pop.

    MazeGenerator(Ticker &shape)
    {
        this->shape = Ticker(shape);
        int prod = 1;
        for (::std::vector<int>::iterator it = this->shape.data.begin(); it != this->shape.data.end(); it++)
        {
            prod *= *it;
        }
        this->data = (unsigned char *)getSpace(prod * sizeof(unsigned char));
        int arr[4] = {0};
        for (int i = 0; i < this->dimension; i++)
        {
            arr[i] = 1;
            this->directions.push_back(Ticker(arr, 4));
            arr[i] = -1;
            this->directions.push_back(Ticker(arr, 4));
            arr[i] = 0;
        }
        this->exploreHistory.push(Ticker(arr, 4));
    }

    MazeGenerator(unsigned char *data, Ticker &shape)
    {
        this->data = data;
        this->shape = Ticker(shape);
        int prod = 1;
        for (::std::vector<int>::iterator it = this->shape.data.begin(); it != this->shape.data.end(); it++)
        {
            prod *= *it;
        }
        this->data[prod - 1];
        this->data = (unsigned char *)getSpace(prod * sizeof(unsigned char));
        int arr[4] = {0};
        for (int i = 0; i < this->dimension; i++)
        {
            arr[i] = 1;
            this->directions.push_back(Ticker(arr, 4));
            arr[i] = -1;
            this->directions.push_back(Ticker(arr, 4));
            arr[i] = 0;
        }
        this->exploreHistory.push(Ticker(arr, 4));
    }

    unsigned char operator[](Ticker &ticker)
    {
        int sum = 0;
        int product = 1;
        for (int i = this->dimension - 1; i >= 0; i--)
        {
            sum += product * ticker[i];
            product *= this->shape[i];
        }
        return this->data[sum];
    }

    void set(Ticker &ticker, unsigned char value)
    {
        int sum = 0;
        int product = 1;
        for (int i = this->dimension - 1; i >= 0; i--)
        {
            sum += product * ticker[i];
            product *= this->shape[i];
        }
        this->data[sum] = value;
    }

    void fillinit()
    {
        int product = 1;
        for (int i = this->dimension - 1; i >= 0; i--)
        {
            product *= this->shape[i];
        }
        memset(this->data, 1, product * sizeof(unsigned char));
    }

    bool legalTicker(Ticker &ticker)
    {
        if (!ticker.dimension)
        {
            return false;
        }
        for (int i = 0; i < this->dimension; i++)
        {
            if (ticker[i] < 0 || ticker[i] >= this->shape[i])
            {
                return false;
            }
        }
        return true;
    }

    ::std::vector<Ticker> neighbors(Ticker &ticker)
    {
        ::std::vector<Ticker> out;
        for (::std::vector<Ticker>::iterator it = this->directions.begin(); it != this->directions.end(); it++)
        {
            Ticker v = ticker + *it;
            if (this->legalTicker(v))
            {
                out.push_back(v);
            }
        }
        return out;
    }

    ::std::vector<Ticker> emptyNeighbors(Ticker &ticker)
    {
        ::std::vector<Ticker> out;
        for (::std::vector<Ticker>::iterator it = this->directions.begin(); it != this->directions.end(); it++)
        {
            Ticker v = ticker + *it;
            if (this->legalTicker(v) && (*this)[v] == 1)
            {
                out.push_back(v);
            }
        }
        return out;
    }

    bool allEmptyNeighbors(Ticker &ticker, Ticker &exc)
    {
        // ::std::cout << "301" << ::std::endl;
        for (::std::vector<Ticker>::iterator it = this->directions.begin(); it != this->directions.end(); it++)
        {
            // ::std::cout << "302" << ::std::endl;
            Ticker v = ticker + *it;
            // ::std::cout<<"303"<<::std::endl;
            // printf("in 3O3 v add: 0x%016X\n", &v);
            // printf("in 3O3 exc add: 0x%016X\n", &exc);
            // printf("exc Dimension:%d, dataSize%d\n", exc.dimension, exc.data.size());
            // fflush(stdout);
            if (v == exc)
            {
                continue;
            }
            // ::std::cout<<"304"<<::std::endl;
            if (this->legalTicker(v) && (*this)[v] == 0)
            {
                return false;
            }
            // ::std::cout<<"305"<<::std::endl;
        }
        return true;
    }

    void dig(Ticker &ticker)
    {
        this->set(ticker, 0);
    }

    void explore(Ticker &ticker)
    {
        // ::std::cout << "200" << ::std::endl;
        if ((*this)[ticker] == 1 && this->allEmptyNeighbors(ticker, this->exploreHistory.top()))
        {
            // ::std::cout << "201" << ::std::endl;
            this->dig(ticker);
            this->exploreHistory.push(ticker);
            ticker._print_me();
            ::std::vector<Ticker> targets = this->neighbors(ticker);
            ::std::stack<Ticker> _funcdeq;
            // ::std::cout << "202" << ::std::endl;
            if (!targets.empty())
            {
                ::std::random_shuffle(targets.begin(), targets.end());
                for (::std::vector<Ticker>::iterator t = targets.begin(); t != targets.end(); t++)
                {
                    _funcdeq.push(*t);
                }
                // ::std::cout << "203" << ::std::endl;
            }
            _funcdeq.push(Ticker());
            while (!_funcdeq.empty())
            {
                this->funcDeque.push_front(_funcdeq.top());
                _funcdeq.pop();
                // ::std::cout << "204" << ::std::endl;
            }
        }
    }

    void _print_me_too()
    {
#if I_WANNA_DEBUG
        printf("myAddress: %X", this->data);
        int arr[4] = {0};
        ::std::string s;
        for (arr[1] = 0; arr[1] < this->shape[1]; arr[1]++)
        {
            for (arr[0] = 0; arr[0] < this->shape[0]; arr[0]++)
            {
                Ticker t(arr, 4);
                s += ::std::to_string((int)(*this)[t]);
                s += ' ';
            }
            s += '\n';
        }
        ::std::cout << s << ::std::endl;
#endif
    }

    void operator()()
    {
        if (!this->result)
        {
            // ::std::cout << "101" << ::std::endl;
            this->fillinit();
            int arr[4] = {0};
            Ticker t = Ticker(arr, 4);
            // ::std::cout << "102" << ::std::endl;
            this->explore(t);
            // ::std::cout << "103" << ::std::endl;
            while (!this->funcDeque.empty())
            {
                Ticker _t = *this->funcDeque.begin();
                this->funcDeque.pop_front();
                // ::std::cout << "104" << ::std::endl;
                if (_t.dimension)
                {
                    // ::std::cout << "1051" << ::std::endl;
                    this->explore(_t);
                    // ::std::cout << "1052" << ::std::endl;
                }
                else
                {
                    this->exploreHistory.pop();
                }
                // ::std::cout << "106" << ::std::endl;
            }
            this->result = true;
        }
    }
};

struct DataParams
{
    unsigned char *data;
    int *shape;
};

extern "C" __declspec(dllexport) void generate(struct DataParams *params)
{

    // ::std::cout << "111" << ::std::endl;
    Ticker t = Ticker(params->shape, 4);
    // ::std::cout << "222" << ::std::endl;
    MazeGenerator mg(params->data, t);
    // ::std::cout << "333" << ::std::endl;
    mg();
    // ::std::cout << "444" << ::std::endl;
    mg._print_me_too();
    // COPY!!!CRITICAL MOVE!!!
    int prod = 1;
    for (int i = 0; i < 4; ++i)
    {
        prod *= params->shape[i];
    }
    memcpy(params->data, mg.data, prod * sizeof(unsigned char));
    // free space
    freeSpace();
    return;
}

int main()
{
    int size[4] = {4, 5, 2, 1};
    Ticker t = Ticker(size, 4);
    MazeGenerator mg(t);
    mg();
    int buf[4] = {0};
    for (buf[0] = 0; buf[0] < 4; buf[0]++)
    {
        for (buf[1] = 0; buf[1] < 5; buf[1]++)
        {
            Ticker t = Ticker(buf, 4);
            printf("%d ", mg[t]);
        }
        printf("\n");
    }
    printf("\n");
    buf[2] = 1;
    for (buf[0] = 0; buf[0] < 4; buf[0]++)
    {
        for (buf[1] = 0; buf[1] < 5; buf[1]++)
        {
            Ticker t = Ticker(buf, 4);
            printf("%d ", mg[t]);
        }
        printf("\n");
    }
    return 0;
}