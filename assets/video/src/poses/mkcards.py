import sys;sys.path.insert(0,"/workspace/gs");import cards
from concurrent.futures import ProcessPoolExecutor
P={"mountain":dict(en=("Mountain Pose","Mountains stay steady and strong, even when the wind blows!","You did Mountain Pose."),
                   es=("Postura de la Montaña","¡Las montañas se quedan firmes y fuertes, aunque sople el viento!","Hiciste la postura de la Montaña.")),
   "tree":dict(en=("Tree Pose","Trees grow strong roots. The deeper the roots, the steadier the tree!","You did Tree Pose."),
               es=("Postura del Árbol","Los árboles crecen raíces fuertes. ¡Mientras más profundas, más firme es el árbol!","Hiciste la postura del Árbol.")),
   "chair":dict(en=("Chair Pose","Your leg muscles are some of the strongest in your body. They help you jump and climb!","You did Chair Pose."),
                es=("Postura de la Silla","Los músculos de tus piernas están entre los más fuertes de tu cuerpo. ¡Te ayudan a saltar y trepar!","Hiciste la postura de la Silla."))}
L={"en":("with Hani","Fun fact!","Nice work!"),"es":("con Hani","¡Dato curioso!","¡Muy bien!")}
def job(a):
    k,lg,part=a; t,w,e=P[k][lg]; sub,fh,nh=L[lg]
    g={"title":cards.title(k,t,sub,6.0),"wis":cards.wisdom(k,fh,w,9.0),"end":cards.endcard(k,nh,e,"HudsonSeed · Hani",6.0)}[part]
    cards.render(g,f"/workspace/gs/{k}_{lg}_{part}.mp4")
if __name__=="__main__":
    jobs=[(k,lg,p) for k in P for lg in L for p in ("title","wis","end")]
    with ProcessPoolExecutor(6) as ex: list(ex.map(job,jobs))
