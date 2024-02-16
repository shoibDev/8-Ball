#include "phylib.h"

phylib_object *phylib_new_still_ball(unsigned char number, phylib_coord *pos) {

    phylib_object *new_still_ball = malloc(sizeof(phylib_object));
    if (new_still_ball == NULL) return NULL;

    new_still_ball->type = PHYLIB_STILL_BALL;

    new_still_ball->obj.still_ball.number = number;
    new_still_ball->obj.still_ball.pos = *pos;

    return new_still_ball;
}

phylib_object *phylib_new_rolling_ball(unsigned char number, phylib_coord *pos, phylib_coord *vel, phylib_coord *acc){

    phylib_object *new_rolling_ball = malloc(sizeof(phylib_object));
    if (new_rolling_ball == NULL) return NULL;

    new_rolling_ball->type = PHYLIB_ROLLING_BALL;
    new_rolling_ball->obj.rolling_ball.number = number;

    new_rolling_ball->obj.rolling_ball.pos = phylib_new_coord(pos->x, pos->y);
    new_rolling_ball->obj.rolling_ball.vel = phylib_new_coord(vel->x, vel->y);
    new_rolling_ball->obj.rolling_ball.acc = phylib_new_coord(acc->x, acc->y);

    return new_rolling_ball;
}

phylib_object *phylib_new_hole( phylib_coord *pos ){

    phylib_object *new_hole = malloc(sizeof(phylib_object));
    if (new_hole == NULL) return NULL;

    new_hole->type = PHYLIB_HOLE;
    new_hole->obj.hole.pos = phylib_new_coord(pos->x, pos->y);

    return new_hole;
}

phylib_object *phylib_new_hcushion( double y ){

    phylib_object *new_hcushion = malloc(sizeof(phylib_object));
    if (new_hcushion == NULL) return NULL;

    new_hcushion->type = PHYLIB_HCUSHION;
    new_hcushion->obj.hcushion.y = y;

    return new_hcushion;
}

phylib_object *phylib_new_vcushion( double x ){

    phylib_object *new_vcushion = malloc(sizeof(phylib_object));
    if (new_vcushion == NULL) return NULL;

    new_vcushion->type = PHYLIB_VCUSHION;
    new_vcushion->obj.vcushion.x = x;

    return new_vcushion;
}


phylib_table *phylib_new_table( void ){

    phylib_table *new_table = malloc(sizeof(phylib_table));
    phylib_coord *bufferCoord = malloc(sizeof(phylib_coord));
 
    if (new_table == NULL || bufferCoord == NULL) return NULL;
  
    new_table->time = 0.0;

    // Add horizontal and vertical cushions
    new_table->object[0] = phylib_new_hcushion(0.0);
    new_table->object[1] = phylib_new_hcushion(PHYLIB_TABLE_LENGTH);
    new_table->object[2] = phylib_new_vcushion(0.0);
    new_table->object[3] = phylib_new_vcushion(PHYLIB_TABLE_WIDTH);
   
    bufferCoord->x = 0.0;
    bufferCoord->y = 0.0;
    new_table->object[4] = phylib_new_hole(bufferCoord); // bottom left hole;

    bufferCoord->x = 0.0;
    bufferCoord->y = PHYLIB_TABLE_WIDTH;
    new_table->object[5] = phylib_new_hole(bufferCoord); // bottom right hole;

    bufferCoord->x = 0.0;
    bufferCoord->y = (PHYLIB_TABLE_LENGTH);
    new_table->object[6] = phylib_new_hole(bufferCoord); // middle left hole;    
    
    bufferCoord->x = PHYLIB_TABLE_WIDTH;
    bufferCoord->y = 0.0;
    new_table->object[7] = phylib_new_hole(bufferCoord); // middle right hole;  

    bufferCoord->x = PHYLIB_TABLE_WIDTH;
    bufferCoord->y = PHYLIB_TABLE_WIDTH;
    new_table->object[8] = phylib_new_hole(bufferCoord); // top left hole;
    
    bufferCoord->x = PHYLIB_TABLE_WIDTH;
    bufferCoord->y = PHYLIB_TABLE_LENGTH;
    new_table->object[9] = phylib_new_hole(bufferCoord); // top right hole;

    // Set the remaining pointers to NULL
    for (int i = 10; i < PHYLIB_MAX_OBJECTS; i++) {
        new_table->object[i] = NULL;
    }

    free(bufferCoord);
    return new_table; 
}

// Part II:
void phylib_copy_object( phylib_object **dest, phylib_object **src ){
    if (src == NULL || *src == NULL) {
        *dest = NULL;
    } else {
        *dest = malloc(sizeof(phylib_object));
        if (*dest == NULL) {
            return;
        }
        memcpy(*dest, *src, sizeof(phylib_object));
    }
}

phylib_table *phylib_copy_table( phylib_table *table ){
    phylib_table *new_table = malloc(sizeof(phylib_table));
    if (new_table == NULL) return NULL;
    
    new_table->time = table->time;

    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        if (table->object[i] != NULL) {
            phylib_copy_object(&new_table->object[i], &table->object[i]);
        } else {
            new_table->object[i] = NULL;
        }
    }
    return new_table;
}

void phylib_add_object(phylib_table *table, phylib_object *object) {
    if (table == NULL || object == NULL) return; 

    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        if (table->object[i] == NULL) {
            table->object[i] = object;
            break; // Exit the loop after adding the object
        }
    }
}

void phylib_free_table(phylib_table *table) {
    if (table == NULL) return;

    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        if (table->object[i] != NULL) {
            free(table->object[i]);
            table->object[i] = NULL;
        }
    }
    free(table);
}

phylib_coord phylib_sub( phylib_coord c1, phylib_coord c2 ){
    return phylib_new_coord((c1.x-c2.x), (c1.y-c2.y));
}

double phylib_length(phylib_coord c) {
    return sqrt(((c.x * c.x) + (c.y * c.y)));
}

double phylib_dot_product(phylib_coord a, phylib_coord b) {
    return ((a.x * b.x) + (a.y * b.y));
}

double phylib_distance( phylib_object *obj1, phylib_object *obj2 ){
    if (obj1 == NULL || obj2 == NULL || obj1->type != PHYLIB_ROLLING_BALL) return -1.0;

    double distance = 0.0;

    phylib_coord obj_1_coord = phylib_new_coord(obj1->obj.rolling_ball.pos.x, obj1->obj.rolling_ball.pos.y); 
    phylib_coord obj_2_coord;

    if(obj2->type == PHYLIB_ROLLING_BALL || obj2->type == PHYLIB_STILL_BALL){

        if(obj2->type == PHYLIB_ROLLING_BALL){
            obj_2_coord = phylib_new_coord(obj2->obj.rolling_ball.pos.x, obj2->obj.rolling_ball.pos.y);
        }else{
            obj_2_coord = phylib_new_coord(obj2->obj.still_ball.pos.x, obj2->obj.still_ball.pos.y);
        }
        
        distance = phylib_length(phylib_sub(obj_1_coord, obj_2_coord)) - PHYLIB_BALL_DIAMETER;

    }else if(obj2->type == PHYLIB_HOLE){

        distance = phylib_length(phylib_sub(obj_1_coord, phylib_new_coord(obj2->obj.hole.pos.x, obj2->obj.hole.pos.y))) - PHYLIB_HOLE_RADIUS;

    }else if(obj2->type == PHYLIB_HCUSHION || obj2->type == PHYLIB_VCUSHION){
        
        if(obj2->type == PHYLIB_HCUSHION){
            distance = fabs(obj_1_coord.y - obj2->obj.hcushion.y) - PHYLIB_BALL_RADIUS;
        }else{
            distance = fabs(obj_1_coord.x - obj2->obj.vcushion.x) - PHYLIB_BALL_RADIUS;
        }
    }
    return distance;
}

// Part III:

void phylib_roll(phylib_object *new, phylib_object *old, double time) {
    if (new == NULL | old == NULL || 
        new->type != PHYLIB_ROLLING_BALL || 
        old->type != PHYLIB_ROLLING_BALL) {
        return;
    }

    // Extract old ball's position, velocity, and acceleration
    phylib_coord pos_old = old->obj.rolling_ball.pos;
    phylib_coord vel_old = old->obj.rolling_ball.vel;
    phylib_coord acc_old = old->obj.rolling_ball.acc;

    // Update new ball's position, velocity and acceloration
    new->obj.rolling_ball.pos.x = pos_old.x + vel_old.x * time + 0.5 * acc_old.x * time * time;
    new->obj.rolling_ball.pos.y = pos_old.y + vel_old.y * time + 0.5 * acc_old.y * time * time;

    new->obj.rolling_ball.vel.x = vel_old.x + acc_old.x * time;
    new->obj.rolling_ball.vel.y = vel_old.y + acc_old.y * time;

    new->obj.rolling_ball.acc.x = acc_old.x;
    new->obj.rolling_ball.acc.y = acc_old.y;

    if((new->obj.rolling_ball.vel.x * old->obj.rolling_ball.vel.x) < 0){
        new->obj.rolling_ball.vel.x = 0;
        new->obj.rolling_ball.acc.x = 0;
    }
    if((new->obj.rolling_ball.vel.y * old->obj.rolling_ball.vel.y) < 0){
        new->obj.rolling_ball.vel.y = 0;
        new->obj.rolling_ball.acc.y = 0;
    }
}

unsigned char phylib_stopped(phylib_object *object) {

    phylib_coord vel = object->obj.rolling_ball.vel;
    double speed = phylib_length(vel);

    phylib_object old_object = *object;

    if (speed < PHYLIB_VEL_EPSILON) {
        object->type = PHYLIB_STILL_BALL;
        object->obj.still_ball.number = old_object.obj.rolling_ball.number;
        object->obj.still_ball.pos = old_object.obj.rolling_ball.pos;
        
        return 1; 
    }

    return 0; 
}

void phylib_bounce( phylib_object **a, phylib_object **b ){

    if( (*b)->type == PHYLIB_HCUSHION){
        (*a)->obj.rolling_ball.vel.y = -((*a)->obj.rolling_ball.vel.y);
        (*a)->obj.rolling_ball.acc.y = -((*a)->obj.rolling_ball.acc.y);
    }else if( (*b)->type == PHYLIB_VCUSHION){
        (*a)->obj.rolling_ball.vel.x = -((*a)->obj.rolling_ball.vel.x);
        (*a)->obj.rolling_ball.acc.x = -((*a)->obj.rolling_ball.acc.x);
    }else if( (*b)->type == PHYLIB_HOLE){
        free((*a));
        (*a) = NULL;
    }else if( (*b)->type == PHYLIB_STILL_BALL){
        phylib_object still_ball_b = **b;

        (*b)->type = PHYLIB_ROLLING_BALL;
        (*b)->obj.rolling_ball.number = still_ball_b.obj.still_ball.number;

        (*b)->obj.rolling_ball.pos = still_ball_b.obj.still_ball.pos;
        (*b)->obj.rolling_ball.vel = phylib_new_coord(0.0, 0.0);
        (*b)->obj.rolling_ball.acc = phylib_new_coord(0.0, 0.0);
    }

    if((*b)->type == PHYLIB_ROLLING_BALL){
       
        phylib_coord r_ab = phylib_sub((*a)->obj.rolling_ball.pos, (*b)->obj.rolling_ball.pos);
        phylib_coord v_rel = phylib_sub((*a)->obj.rolling_ball.vel, (*b)->obj.rolling_ball.vel);

        double r_ab_length = phylib_length(r_ab);
        phylib_coord n = phylib_new_coord(r_ab.x / r_ab_length, r_ab.y / r_ab_length);

        double v_rel_n = phylib_dot_product(v_rel, n);

        (*a)->obj.rolling_ball.vel.x -= v_rel_n * n.x;
        (*a)->obj.rolling_ball.vel.y -= v_rel_n * n.y;

        (*b)->obj.rolling_ball.vel.x += v_rel_n * n.x;
        (*b)->obj.rolling_ball.vel.y += v_rel_n * n.y;
        
        double speed = phylib_length((*a)->obj.rolling_ball.vel);
        if (speed > PHYLIB_VEL_EPSILON) {
            (*a)->obj.rolling_ball.acc.x = -((*a)->obj.rolling_ball.vel.x / speed) * PHYLIB_DRAG;
            (*a)->obj.rolling_ball.acc.y = -((*a)->obj.rolling_ball.vel.y / speed) * PHYLIB_DRAG;
        }

        speed = phylib_length((*b)->obj.rolling_ball.vel);
        if (speed > PHYLIB_VEL_EPSILON) {
            (*b)->obj.rolling_ball.acc.x = -((*b)->obj.rolling_ball.vel.x / speed) * PHYLIB_DRAG;
            (*b)->obj.rolling_ball.acc.y = -((*b)->obj.rolling_ball.vel.y / speed) * PHYLIB_DRAG;
        }
    }
}

unsigned char phylib_rolling(phylib_table *t) {
    if (t == NULL) return 0;
    
    unsigned char rolling_ball_count = 0;

    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        if (t->object[i] != NULL && t->object[i]->type == PHYLIB_ROLLING_BALL) {
            rolling_ball_count++;
        }
    }

    return rolling_ball_count;
}

phylib_table *phylib_segment(phylib_table *table) {
    if (table == NULL || phylib_rolling(table) == 0) return NULL;

    phylib_table *segment = phylib_copy_table(table);
    if (segment == NULL) return NULL;

    for(double time = PHYLIB_SIM_RATE; time <= PHYLIB_MAX_TIME; time += PHYLIB_SIM_RATE){
        segment->time += PHYLIB_SIM_RATE;
        for(int i = 0; i < PHYLIB_MAX_OBJECTS; i++){
            if(segment->object[i] != NULL && segment->object[i]->type == PHYLIB_ROLLING_BALL){
                phylib_roll(segment->object[i], table->object[i], time);
            }
        }
        for(int i = 0; i < PHYLIB_MAX_OBJECTS; i++){
            if(segment->object[i] != NULL && segment->object[i]->type == PHYLIB_ROLLING_BALL){
                for(int j = 0; j < PHYLIB_MAX_OBJECTS; j++){
                    if (i != j && segment->object[j] != NULL && segment->object[i] != NULL){
                        double distance = phylib_distance(segment->object[i], segment->object[j]);
                        if(distance < 0.0){
                            phylib_bounce(&(segment->object[i]), &(segment->object[j]));
                            return segment; 
                        }
                    }
                }
                if (phylib_stopped(segment->object[i])) {
                    return segment; 
                } 
            }
        }
    }
    return segment;
}

char *phylib_object_string(phylib_object *object)
{
    static char string[80];
    if (object == NULL)
    {
        snprintf(string, 80, "NULL;");
        return string;
    }

    switch (object->type)
    {
    case PHYLIB_STILL_BALL:
        snprintf(string, 80, "STILL_BALL (%d,%6.1lf,%6.1lf)", object->obj.still_ball.number, object->obj.still_ball.pos.x,
                 object->obj.still_ball.pos.y);
        break;
    case PHYLIB_ROLLING_BALL:
        snprintf(string, 80,
                 "ROLLING_BALL (%d,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf)",
                 object->obj.rolling_ball.number,
                 object->obj.rolling_ball.pos.x,
                 object->obj.rolling_ball.pos.y,
                 object->obj.rolling_ball.vel.x,
                 object->obj.rolling_ball.vel.y,
                 object->obj.rolling_ball.acc.x,
                 object->obj.rolling_ball.acc.y);
        break;
    case PHYLIB_HOLE:
        snprintf(string, 80,
                 "HOLE (%6.1lf,%6.1lf)",
                 object->obj.hole.pos.x,
                 object->obj.hole.pos.y);
        break;
    case PHYLIB_HCUSHION:
        snprintf(string, 80,
                 "HCUSHION (%6.1lf)",
                 object->obj.hcushion.y);
        break;
    case PHYLIB_VCUSHION:
        snprintf(string, 80,
                 "VCUSHION (%6.1lf)",
                 object->obj.vcushion.x);
        break;
    }
    return string;
}

// Helper methods:
phylib_coord phylib_new_coord(double x, double y){
    phylib_coord new_coord;

    new_coord.x = x;
    new_coord.y = y;

    return new_coord;
}
