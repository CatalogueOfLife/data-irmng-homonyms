from bs4 import BeautifulSoup
import re, csv ,glob


def normWS(x):
  return re.sub(r'[\x00-\x20\xA0\xAD]+',' ', x).strip()

class Name:

  counter = 0
  nomStats = {}
  
  def __init__(self, rank, a, search):
    #print(a.text)
    m = re.search('id=([0-9]+)', a['href'])
    self.id = m.group(1)
    self.rank = rank
    self.name = None
    self.author = None
    self.accepted = None
    self.status = 'accepted'
    self.nomstatus = None
    self.classification = None

    i=a.find('i')
    if i:
      self.name = normWS(i.text)
      au=i.next_sibling
      if au:
        self.author = normWS(au)
    else:
      self.name = normWS(a.text)
    if search:
      for x in a.next_siblings:
        if x.name == 'a' and x.text.strip():
          self.accepted = Name(self.rank, x, False)
          # some names refer to themselves as the synonym & accepted - ignore!
          if self.accepted.id == self.id:
            self.accepted=None
          else:
            self.status='synonym'
        elif x.name == 'span':
          if 'uncertain' in x.text:
            self.status = 'provisionally accepted'
          else:
            self.nomstatus=x.text
            if self.nomstatus in Name.nomStats:
              Name.nomStats[self.nomstatus] += 1
            else:
              Name.nomStats[self.nomstatus] = 1
            print(self.name, self.nomstatus)
        elif x.name == 'small':
          self.classification = x.text
        elif x.name == 'br':
          break
  
  def write(self, w):
    status = 'accepted'
    pid = None
    if self.accepted:
      w.writerow([self.accepted.id, None, status, self.nomstatus, self.accepted.rank, self.accepted.name, self.accepted.author, self.classification])
      Name.counter += 1
      status = 'synonym'
      pid = self.accepted.id
    w.writerow([self.id, pid, status, self.nomstatus, self.rank, self.name, self.author, self.classification])
    Name.counter += 1

  def __str__(self):
    acc = " acc: %s" % self.accepted if self.accepted else ""
    return "%s %s [%s]%s" % (self.name, self.author, self.id, acc)



def processFile(rank, fn):
  counterBefore = Name.counter
  print("Reading %s" % fn)
  with open(fn, "r", encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')
    for br in soup.body.find_all('br'):
      for x in br.next_siblings:
        if x.name == 'a':
          n = Name(rank, x, True)
          n.write(w)
          break
        elif x.name == 'br':
          break
  print("  added %s names" % (Name.counter-counterBefore))




with open("NameUsage.csv", "w", encoding='utf-8') as csvf:
  w = csv.writer(csvf)
  header = ['ID', 'parentID', 'status', 'nameStatus', 'rank', 'scientificName', 'authorship', 'remarks']
  w.writerow(header)

  processFile('family', 'family.html')
  for fn in glob.glob("genus*.html"):
    processFile('genus', fn)
  for fn in glob.glob("species*.html"):
    processFile('species', fn)
print("Finished. Written %s names to NameUsage.csv" % Name.counter)
print("Name statuses found: %s" % Name.nomStats)



