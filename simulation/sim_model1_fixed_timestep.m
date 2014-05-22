clear all; close all; clc;
% Codes for ECS289F - "Opinion dynamics w/ reluctant agents"
% Feel free to play around with it...

N = 5;
A = ones(N) - eye(N); % This is a fully connected graph
iter_max = 5e2; % the max. no. of iterations 

flag = 0; % if flag = 0, run the standard reluctant agent model -> results in biased average
% if flag = 1, then the agents will "delay" until making the next update.
% In this case, the reluctant model will find the true average.

% Specify the adaptivity of the agents
tau_x = 1*ones(N,1); 
tau_x(1:1) = 5; % select the reluctant agents. WLOG, we always assume the reluctant agent are the first

the_vector = zeros(N,100);
% for monte_carlo = 1 : 100
x0 = [0 2 2 2 2];
x0(1) = 10;
x0 = x0';
x_avg = mean(x0); 

% Init. the algorithms
x_gossip = x0; x_model1 = x0; xh_model1 = x0; xo_model1 = x0;
cnt_xh = ones(N,1);
sq_dist_gos = zeros(iter_max,1); sq_dist_model1 = sq_dist_gos;

x_augment = zeros(N + 2*sum(tau_x>1),1); x_augment(1:N) = x0;
cnt_anal = 100*ones(N,1);
A_accum = zeros(length(x_augment),length(x_augment),2*iter_max);

fixed_list = [ 1 2; 2 3; 3 4; 1 5; 2 4; 3 4; 4 5; 2 3; 3 5; 4 5];

for iter_no = 1 : iter_max
    % A random node wake up at this time
%     src_node = randint(1,1,[1 N]);
%     % It selects a random neighbor with uniform probability
%     pos_set = [1:src_node-1 src_node+1:N];
%     pos_choice = find(A(src_node,pos_set)>0);
%     dst_node_idx = randint(1,1,[1 length(pos_choice)]);
%     dst_node = pos_set(dst_node_idx);
    src_node = fixed_list(iter_no,1); 
    dst_node = fixed_list(iter_no,2); 

    
    % Baseline: the two nodes communicates and update opinions instantly
    tmp_avg = (x_gossip(src_node) + x_gossip(dst_node))/2;
    x_gossip(src_node) = tmp_avg;
    x_gossip(dst_node) = tmp_avg;
    
    % For benchmarking: evaluate the square distance
    sq_dist_gos(iter_no) = sqrt(sum( (x_gossip-x_avg).^2 ));
    
    % Model 1 with reluctant agent
    cnt_xh = cnt_xh + 1;
    cnt_xh = min( tau_x, cnt_xh ); % such that the counter is bounded
    
    if ( (mod(iter_no,10) == 0) || (flag == 0) )
        cnt_xh(src_node) = 1; cnt_xh(dst_node) = 1; % reset the counters
        xo_model1(src_node) = x_model1(src_node); xo_model1(dst_node) = x_model1(dst_node);
        % tmp_avg is the average of the two agents' opinion
        tmp_avg = (x_model1(src_node) + x_model1(dst_node))/2;
        % xh_model1 corresponds to the \hat{x} in the writeup
        xh_model1(src_node) = tmp_avg; xh_model1(dst_node) = tmp_avg;
    end

    % we now evaluate the updates for both agents according to the
    % designed rule
    for n = 1 : N
        x_model1(n) = (cnt_xh(n)/tau_x(n))*xh_model1(n) + ...
            ((tau_x(n)-cnt_xh(n))/tau_x(n))*xo_model1(n);
    end
    
    % eval. the squared distance now
    sq_dist_model1(iter_no) = sqrt(sum( (x_model1-x_avg).^2 ));
    
    % Describe the opinion dynamics using the augmented model
    cnt_anal = cnt_anal + 1;
    cnt_anal(src_node) = 1; cnt_anal(dst_node) = 1;
    A_current = eye(length(x_augment));
    if src_node <= max(find(tau_x>1))
        A_current(2*src_node-1+N,2*src_node-1+N) = 0;
        A_current(2*src_node-1+N,src_node) = 0.5; A_current(2*src_node-1+N,dst_node) = 0.5;
    else
        A_current(src_node,src_node) = 0.5; A_current(src_node,dst_node) = 0.5;
    end
    if dst_node <= max(find(tau_x>1))
        A_current(2*dst_node-1+N,2*dst_node-1+N) = 0;
        A_current(2*dst_node-1+N,src_node) = 0.5; A_current(2*dst_node-1+N,dst_node) = 0.5;
    else
        A_current(dst_node,src_node) = 0.5; A_current(dst_node,dst_node) = 0.5;
    end
    for rel_node = 1 : max(find(tau_x>1))
        if cnt_anal(rel_node) == 1
            A_current(2*rel_node+N,2*rel_node+N) = 0;
            A_current(2*rel_node+N,rel_node) = 1; % I store the value here..
        end
    end
    A_accum(:,:,2*iter_no-1) = A_current;
    
    % Now the adaptation stage
    A_current = eye(length(x_augment));
    for rel_node = 1 : max(find(tau_x>1))
        if cnt_anal(rel_node) <= tau_x(rel_node)
            A_current(rel_node,rel_node) = 0;
            A_current(rel_node,2*rel_node-1+N) = cnt_anal(rel_node)/tau_x(rel_node); 
            A_current(rel_node,2*rel_node+N) = (tau_x(rel_node)-cnt_anal(rel_node))/tau_x(rel_node); 
        end
    end
    A_accum(:,:,2*iter_no) = A_current;
    
    x_augment = A_accum(:,:,2*iter_no)*A_accum(:,:,2*iter_no-1)*x_augment;
    
    x_model1
end

% fprintf('Sq. Dist to true average (baseline): %f ||',sq_dist_gos(end));
% fprintf('Sq. Dist to true average (Model1): %f \n',sq_dist_model1(end));

% semilogy(1:iter_max,sq_dist_gos,1:iter_max,sq_dist_model1)

A_recursive = A_accum(:,:,1);
for iii = 2 : 2*iter_max
    A_recursive = A_accum(:,:,iii)*A_recursive;
end
the_vector(:,monte_carlo) = A_recursive(1,1:N);

% end
% 
% mean(the_vector')