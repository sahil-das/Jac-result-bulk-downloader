import requests;

url = 'https://www.jacresults.com/science/show_result.php'

#datail of students
school_name="xaviers ranchi"
roll_code=11062
start_roll_no=10001
last_roll_no=10750
total_result_in_one_file =250


k=1
start_file_name=start_roll_no

if (last_roll_no - start_roll_no <= total_result_in_one_file ):
    
    end_file_name=last_roll_no
    
else:
    end_file_name=start_file_name +(total_result_in_one_file-1)


#url = "https://www.google.com"
for i in range(start_roll_no,last_roll_no+1):
                
                try:
                    print("Downloading.......  Roll No-",i)
                    my_data = { 'rollcode': roll_code  ,'rollno':i }
                    x = requests.post("https://www.jacresults.com/science/show_result.php", data = my_data)
                    
                  #  print(x.text)
                    print("Downloaded Roll No.- ",i)
                    myfile=school_name+" Results from Roll No-"+str(start_file_name)+" to Roll No.-"+str(end_file_name)+".html"
                    f = open(myfile, "a")
                    f.write(x.text)
                    print("Roll No.- ",i," saved","\n")
                   
                except:
                    print("Not downloaded Roll No. - ",i ,"\n")
         
                
                if(k==total_result_in_one_file):
                   #print("main if ")
                    start_file_name=end_file_name + 1
                    
                    if(last_roll_no - i <total_result_in_one_file):
                     #  print("last_roll_no")
                       end_file_name=last_roll_no
                    else:
                        
                       #print("sahil")       
                       end_file_name=start_file_name+(total_result_in_one_file-1)
                    k=1
                   # print("k=1")
                    
                else:
                #    print("main else")
                    k=k+1