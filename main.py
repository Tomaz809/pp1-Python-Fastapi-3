from typing import Annotated

from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI()

app.title = "Cartelera - Cuevana"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

NOT_FOUND_RESPONSE = {
    404: {
        "description": "Película no encontrada en el sistema",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Pelicula no encontrada",
                }
            }
        },
    },
}

IdPelicula = Annotated[int, Path(gt=0, description="El ID debe ser un entero mayor a 0")]
TextoValidado = Annotated[str, Field(min_length=2, max_length=50)]
CalidadValidada = Annotated[float, Field(ge=0, le=5, description="Calidad de la película entre 0 y 5")]
HorarioValidado = Annotated[str, Field(min_length=4, max_length=5, description="Formato HH:MM")]

class PeliculaSchema(BaseModel):
    id: Annotated[int, Field(gt=0, description="ID único de la película")]
    titulo: TextoValidado
    categoria: TextoValidado
    productor: TextoValidado
    calidad: CalidadValidada
    horario: HorarioValidado
    activo: bool = True

class PeliculaUpdateSchema(BaseModel):
    titulo: TextoValidado
    categoria: TextoValidado
    productor: TextoValidado
    calidad: CalidadValidada
    horario: HorarioValidado
    activo: bool = True


peliculas = [
    {"id": 1, "titulo": "Bend It Like Beckham", "categoria": "comedia", "productor": "Kihn, Reichert and Heidenreich", "calidad": 4, "horario": "18:00", "activo": True},
    {"id": 2, "titulo": "Red Riding: 1983", "categoria": "drama", "productor": "Hansen-Okuneva", "calidad": 3, "horario": "20:30", "activo": True},
    {"id": 3, "titulo": "School of Rock", "categoria": "musical", "productor": "Hintz, Mraz and Bins", "calidad": 5, "horario": "22:00", "activo": False},
    {"id": 4, "titulo": "The Great Northfield Minnesota Raid", "categoria": "western", "productor": "Paucek-Luettgen", "calidad": 2, "horario": "17:15", "activo": False},
    {"id": 5, "titulo": "Bandaged", "categoria": "suspenso", "productor": "O'Connell Inc", "calidad": 3, "horario": "19:45", "activo": True},
    {"id": 6, "titulo": "Away from Her", "categoria": "romance", "productor": "Konopelski Group", "calidad": 4, "horario": "21:00", "activo": False},
    {"id": 7, "titulo": "Foreign Letters", "categoria": "drama", "productor": "Bernier-Connelly", "calidad": 2, "horario": "16:30", "activo": False},
    {"id": 8, "titulo": "American Astronaut, The", "categoria": "ciencia ficción", "productor": "Crooks-Skiles", "calidad": 5, "horario": "23:15", "activo": False},
    {"id": 9, "titulo": "Billu", "categoria": "comedia", "productor": "Connelly-Powlowski", "calidad": 3, "horario": "19:00", "activo": True},
    {"id": 10, "titulo": "Once Upon a Honeymoon", "categoria": "romance", "productor": "Hahn, Sporer and Bernier", "calidad": 4, "horario": "20:00", "activo": False}
]

@app.get("/")
def home():
    return {"message": "Welcome to Cuevana!"}


@app.get("/cartelera", response_model=list[PeliculaSchema])
async def movies():
    peliculasActivas = []
    for p in peliculas:
        if(p['activo']):
            peliculasActivas.append(p)
    return peliculasActivas


@app.get("/movie/{id}", responses=NOT_FOUND_RESPONSE, response_model=PeliculaSchema)
async def buscarPelicula(id: IdPelicula):
    for movie in peliculas:
        if movie["id"] == id:
            return movie
    raise HTTPException(status_code=404, detail="Pelicula no encontrada")


@app.post("/Movie-nueva", response_model=PeliculaSchema)
async def nuevaPelicula(nueva_pelicula: PeliculaSchema):
    peliculas.append(nueva_pelicula.model_dump())
    return nueva_pelicula


@app.put("/modificar-peliculas/{id}", responses=NOT_FOUND_RESPONSE, response_model=PeliculaSchema)
async def editar_pelicula(
    id: IdPelicula,
    pelicula_editar: PeliculaUpdateSchema
):
    for m in peliculas:
        if m["id"] == id:            
            m["titulo"] = pelicula_editar.titulo
            m["categoria"] = pelicula_editar.categoria
            m["productor"] = pelicula_editar.productor
            m["calidad"] = pelicula_editar.calidad
            m["horario"] = pelicula_editar.horario
            m["activo"] = pelicula_editar.activo
            return m
    raise HTTPException(status_code=404, detail="Pelicula no encontrada")


@app.delete("/movie/{id}", responses=NOT_FOUND_RESPONSE, response_model=PeliculaSchema)
async def borrar_pelicula(
    id: IdPelicula,
    logico: Annotated[bool, Query(description="¿True para desactivar, False para eliminar físicamente?")] = False
):
    for a in peliculas:
        if a["id"] == id:
            if logico:
                a["activo"] = False
            else:
                peliculas.remove(a)
            return a
            
    raise HTTPException(status_code=404, detail="Pelicula no encontrada")