

print("hello world")
#simple if else statement
if 5 < 2:
    print("5 is greater than 2")
else:
    print("5 is not greater than 2")

    #comment


#simple math
    x=5
    y=10
    print(x)
    print(y+x)

    if x * y ==100:
        print("this is true")
    else:
        print("this is false  becuase this is the correct answer " + str(x*y))


# this prints on the same line use end=" " in the first print statement
    print("i will try to print this on the same line", end=" ")
    print("this is on the same line")


#simple numbers
print(10)
print (3+3)

#simple variables
x=5
y= "nate"

print(x)
print(y)
#print(x+y) # this will give an error because you cannot add a string and an integer together
print(str(y) + str(x))
print(type(x))
print(type(y))
print(x,y)

#case sensitivity
a="nate"
A="khloe"

print(a)
print(A)
print(a + " + " + A)

#python variables
my_variable = "this is a variable"
print(my_variable)
_another_variable = "this is another variable"
print(_another_variable)

#collection

fruits = ["apple", "banana", "cherry"]
vegitables= ["carrots","leeks" ,"broccoli"]
x, y, z = fruits
a,b,c,= vegitables
print(x, end=""),print(a)
print(y)
print(z)
print(b)
print(c)
print(x+"  "+a)
print(vegitables[0])
#global variable
x="global"
y="variable"

def my_func():
     print("this is a "+x+" "+y)
my_func()

response = requests.get(
    f"{BASE_URL}/leagues",
    params={"id": 1, "season": 2022},
    headers={"x-apisports-key": API_KEY}
)
print("Requests remaining:", response.headers.get("x-ratelimit-requests-remaining"))