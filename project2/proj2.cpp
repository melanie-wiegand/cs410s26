#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <stdexcept>

using namespace std;

// ─── VTK Reader ────────────────────────────────────────────────────────────────

struct RectilinearGrid {
    int dims[3];
    vector<float> X, Y, Z;
    vector<float> F;
};

void CheckRectilinearGrid(RectilinearGrid &rg)
{
    if (rg.dims[0] <= 0 || rg.dims[1] <= 0 || rg.dims[2] < 0)
    {
        std::cerr << "Invalid dims: " << rg.dims[0] << "x" << rg.dims[1] << "x" << rg.dims[2] << std::endl;
    }
    if (rg.X.size() != rg.dims[0])
    {
        std::cerr << "Incorrect number of X coordinates." << std::endl;
    }
    if (rg.Y.size() != rg.dims[1])
    {
        std::cerr << "Incorrect number of Y coordinates." << std::endl;
        std::cerr << "Y values = " << rg.Y.size() << ", while dims[1] = " << rg.dims[1] << std::endl;
    }
    if (rg.Z.size() != rg.dims[2])
    {
        std::cerr << "Incorrect number of Z coordinates." << std::endl;
    }
    int numF = rg.dims[0]*rg.dims[1]*(rg.dims[2] >= 1 ? rg.dims[2] : 1);
    if (rg.F.size() != numF)
    {
        std::cerr << "Incorrect number of field values." << std::endl;
    }
}
void ReadCoords(ifstream &f, vector<float> &coords, int n) {
    //string type;
    //f >> type; // e.g. "float"
    coords.resize(n);
    for (int i = 0; i < n; ++i) f >> coords[i];
    string remainder;
    getline(f, remainder);
}

RectilinearGrid ReadVTKRectilinearGrid(const string &filename) {
    ifstream f(filename.c_str());   // c_str() needed pre-C++11
    if (!f.is_open())
        throw runtime_error("Cannot open file: " + filename);

    RectilinearGrid grid;
    grid.dims[0] = grid.dims[1] = grid.dims[2] = 1;

    string line;
    for (int i = 0; i < 4; ++i) getline(f, line); // skip header

    while (getline(f, line)) {
        if (line.empty()) continue;

        istringstream ss(line);
        string keyword;
        ss >> keyword;

        if (keyword == "DIMENSIONS") {
            ss >> grid.dims[0] >> grid.dims[1] >> grid.dims[2];

        } else if (keyword == "X_COORDINATES") {
            int n; ss >> n;
            ReadCoords(f, grid.X, n);

        } else if (keyword == "Y_COORDINATES") {
            int n; ss >> n;
            ReadCoords(f, grid.Y, n);

        } else if (keyword == "Z_COORDINATES") {
            int n; ss >> n;
            ReadCoords(f, grid.Z, n);

        } else if (keyword == "SCALARS") {
            //getline(f, line);  // finish current line
            string ltLine;
            while (getline(f, ltLine))
                if (!ltLine.empty()) break;
            //getline(f, ltLine); // LOOKUP_TABLE line

            int total = grid.dims[0] * grid.dims[1] * grid.dims[2];
            grid.F.resize(total);
            for (int i = 0; i < total; ++i) f >> grid.F[i];
        }
    }

    return grid;
}

// ****************************************************************************
//  Function: CountNumberOfCellsWithinThreshold
//
//  Arguments:
//     X: an array (size is specified by dims).  
//              This contains the X locations of a rectilinear mesh.
//     Y: an array (size is specified by dims).  
//              This contains the Y locations of a rectilinear mesh.
//     dims: an array of size two.  
//              The first number is the size of the array in argument X, 
//              the second the size of Y.
//     F: a scalar field defined on the mesh.  Its size is dims[0]*dims[1].
//     L: the minimum range for a threshold
//     H: the maximum range for a threshold
//
//  Returns:  the number of cells within a threshold range.
//
//  Example: assume the desired threshold range is (L, H).  Consider cell C,
//    which has 4 vertices, and assume these 4 vertices have values F1, F2,
//    F3, and F4.
//    Then we define C to be within the threshold range if:
//       L <= F1 <= H  *AND*
//       L <= F2 <= H  *AND*
//       L <= F3 <= H  *AND*
//       L <= F4 <= H 
//
//   Your goal is to count the number of cells that are within the threshold
//   range. 
//
// ****************************************************************************

int CountNumberOfCellsWithinThreshold(const float *X, const float *Y,
                                      const int *dims, const float *F,
                                      float lower, float upper)
{
    int count = 0;
    // IMPLEMENT ME!
    return count;
}

// ****************************************************************************
//  Function: AreaForCell
//
//  Arguments:
//     X: an array (size is specified by dims).  
//              This contains the X locations of a rectilinear mesh.
//     Y: an array (size is specified by dims).  
//              This contains the Y locations of a rectilinear mesh.
//     dims: an array of size two.  
//              The first number is the size of the array in argument X, 
//              the second the size of Y.
//     cellId: a cellIndex (I.e., between 0 and GetNumberOfCells(dims))
//  
//  Returns:  the area of the cell.  Each cell is a rectangle, and the
//            area of a rectangle is width*height.
//            If an invalid cell is specified, then the function should return 0.
//
// ****************************************************************************

float AreaForCell(const float *X, const float *Y, const int *dims, int cellId)
{
    // IMPLEMENT ME!
    
    return dims[0]*dims[1];
}

// ****************************************************************************
//  Function: EvaluateFieldAtLocation
//
//  Arguments:
//     pt: a two-dimensional location
//     dims: an array of size two.  
//           The first number is the size of the array in argument X, 
//           the second the size of Y.
//     X: an array (size is specified by dims).  
//        This contains the X locations of a rectilinear mesh.
//     Y: an array (size is specified by dims).  
//        This contains the Y locations of a rectilinear mesh.
//     F: a scalar field defined on the mesh.  
//        Its size is dims[0]*dims[1].
//
//   Returns: the interpolated field value. 0 if the location is out of bounds.
//
// ****************************************************************************


float EvaluateFieldAtLocation(const float *pt, const int *dims,
                               const float *X, const float *Y, const float *F)
{
    // IMPLEMENT ME!
    return 0;
}

// ─── Main ─────────────────────────────────────────────────────────────────────

int main()
{
    RectilinearGrid grid;
    try {
        grid = ReadVTKRectilinearGrid("proj2_data.vtk");
    } catch (const exception &e) {
        cerr << "Error: " << e.what() << endl;
        return 1;
    }
    CheckRectilinearGrid(grid);

    int   *dims = grid.dims;
    float *X    = &(grid.X[0]);   
    float *Y    = &(grid.Y[0]);
    float *F    = &(grid.F[0]);

    float ranges[10] = { -1, 1, -1, 0, 0, 1, -0.75f, -0.25f, 0.25f, 0.75f };
    for (int i = 0; i < 5; ++i) {
        int n = CountNumberOfCellsWithinThreshold(X, Y, dims, F,
                                                  ranges[2*i], ranges[2*i+1]);
        cerr << "The number of cells between " << ranges[2*i]
             << " and " << ranges[2*i+1] << " is " << n << endl;
    }

    const int ncells = 5;
    int cellIds[ncells] = { 0, 50, 678, 1000, 1200 };
    for (int i = 0; i < ncells; ++i) {
        float area = AreaForCell(X, Y, dims, cellIds[i]);
        cerr << "The area for cell " << cellIds[i] << " is " << area << endl;
    }

    const int npts = 10;
    float pt[npts][3] = {
        {1.01119f,   0.122062f,  0},
        {0.862376f,  1.33829f,   0},
        {0.155026f,  0.126123f,  0},
        {0.69736f,   0.0653565f, 0},
        {0.2f,       0.274117f,  0},
        {0.893699f,  1.04111f,   0},
        {0.608791f, -0.0533753f, 0},
        {1.00543f,   0.158024f,  0},
        {0.384158f, -0.0768977f, 0},
        {0.666757f,  0.60259f,   0},
    };
    for (int i = 0; i < npts; ++i) {
        float fval = EvaluateFieldAtLocation(pt[i], dims, X, Y, F);
        cerr << "Evaluated field at (" << pt[i][0] << "," << pt[i][1]
             << ") as " << fval << endl;
    }

    cerr << "Infinite loop here, else Windows people may have the terminal "
         << "disappear before they see the output."
         << " Remove these lines if they annoy you." << endl;
    cerr << "(press Ctrl-C to exit program)" << endl;
    while (1);
}
