import cadre_model 

print("This is the main file")

def main():
    model = cadre_model.Model(n=100, verbose=True)
    model.run(MAXTIME=50)
  
if __name__ == "__main__":
    main()
    
        